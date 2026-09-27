"""
Tests for the order service.
"""
import pytest
from unittest.mock import MagicMock, patch
from sample_repo.orders.service import create_order, get_orders_for_user, get_order_summary
from sample_repo.models import Order, User


@pytest.fixture
def mock_user():
    u = MagicMock(spec=User)
    u.id = 7   # Integer ID
    return u


@pytest.fixture
def mock_order():
    o = MagicMock(spec=Order)
    o.id = 1
    o.user_id = 7   # Integer FK to User.id
    o.total_amount = 99.99
    o.status = "pending"
    return o


def test_get_orders_for_user_filters_by_integer_user_id(mock_order):
    """Orders should be retrieved using Integer user_id FK."""
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [mock_order]
    orders = get_orders_for_user(db, user_id=7)
    assert len(orders) == 1
    assert orders[0].user_id == 7


def test_create_order_validates_user_exists():
    """create_order should raise if user_id does not exist."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError, match="not found"):
        create_order(db, user_id=999, total_amount=50.0)


def test_order_summary_uses_integer_user_id(mock_order):
    """get_order_summary returns a dict with integer user_id."""
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [mock_order]
    summary = get_order_summary(db, user_id=7)
    assert summary["user_id"] == 7
    assert isinstance(summary["user_id"], int)


def test_order_user_id_fk_is_integer(mock_order):
    """order.user_id should be Integer FK — will break after UUID migration."""
    assert isinstance(mock_order.user_id, int), \
        "order.user_id is Integer FK. Migrate after User.id UUID change."
