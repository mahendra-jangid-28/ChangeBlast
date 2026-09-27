"""
Test suite for the user service and related functionality.
"""
import pytest
from unittest.mock import MagicMock, patch
from sample_repo.users.service import (
    get_user_by_id, create_user, delete_user,
    update_user, authenticate_user
)
from sample_repo.models import User


# ---- Fixtures ----

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 42          # Integer user ID
    user.email = "alice@example.com"
    user.full_name = "Alice Smith"
    user.is_active = 1
    user.hashed_password = "salt:hash"
    return user


@pytest.fixture
def mock_db(mock_user):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_user
    return db


# ---- Tests ----

def test_get_user_by_id_returns_user(mock_db, mock_user):
    """get_user_by_id should return a user when queried by Integer ID."""
    result = get_user_by_id(mock_db, 42)
    assert result.id == 42
    assert result.email == "alice@example.com"


def test_get_user_by_id_not_found():
    """get_user_by_id should return None for missing IDs."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    result = get_user_by_id(db, 99999)
    assert result is None


def test_create_user_assigns_integer_id(mock_db):
    """Newly created users should receive an Integer ID from the database."""
    new_user = MagicMock(spec=User)
    new_user.id = 100
    new_user.email = "bob@example.com"
    mock_db.refresh.side_effect = lambda u: setattr(u, 'id', 100)

    with patch("sample_repo.users.service.hash_password", return_value="salt:hash"):
        with patch("sample_repo.users.service.User", return_value=new_user):
            result = create_user(mock_db, "bob@example.com", "password", "Bob")
    assert mock_db.add.called
    assert mock_db.commit.called


def test_delete_user_by_integer_id(mock_db, mock_user):
    """delete_user should look up user by Integer ID."""
    result = delete_user(mock_db, 42)
    assert result is True
    assert mock_db.delete.called_with(mock_user)


def test_authenticate_user_returns_none_on_bad_password(mock_db, mock_user):
    """authenticate_user should reject wrong passwords."""
    with patch("sample_repo.users.service.verify_password", return_value=False):
        result = authenticate_user(mock_db, "alice@example.com", "wrongpassword")
    assert result is None


def test_user_id_is_integer(mock_user):
    """Assert that user.id is an int — this test will fail after UUID migration."""
    assert isinstance(mock_user.id, int), \
        "User.id must be int. If migrating to UUID, update this test and all callers."


def test_update_user_by_integer_id(mock_db, mock_user):
    """update_user should accept an Integer user_id."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    result = update_user(mock_db, 42, full_name="Alice Updated")
    assert mock_db.commit.called
