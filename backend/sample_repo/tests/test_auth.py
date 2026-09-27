"""
Tests for auth/security module.
"""
import pytest
from unittest.mock import MagicMock
from sample_repo.auth.security import (
    hash_password, verify_password, build_user_jwt_payload
)
from sample_repo.models import User


def test_hash_and_verify_password():
    """Password hashing round-trip should work."""
    pwd = "supersecret"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_payload_sub_is_string_of_integer():
    """
    JWT payload 'sub' must be str(user.id).
    After UUID migration, this will still be str but the value changes format.
    """
    user = MagicMock(spec=User)
    user.id = 42
    user.email = "test@example.com"
    payload = build_user_jwt_payload(user)
    assert payload["sub"] == "42"
    assert payload["email"] == "test@example.com"


def test_create_session_stores_integer_user_id():
    """Session token creation should persist Integer user_id to DB."""
    db = MagicMock()
    from sample_repo.auth.security import create_session_token
    import sample_repo.auth.security as sec
    from sample_repo.models import UserSession

    token = create_session_token(db, user_id=5)
    assert isinstance(token, str)
    assert len(token) > 10
    assert db.add.called
    assert db.commit.called
