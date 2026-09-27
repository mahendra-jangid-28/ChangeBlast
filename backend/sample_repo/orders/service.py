"""
Order service — handles order creation and retrieval.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sample_repo.models import Order, User


def create_order(db: Session, user_id: int, total_amount: float) -> Order:
    """
    Create a new order for a user.
    user_id must match User.id (Integer FK).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with id={user_id} not found")

    order = Order(user_id=user_id, total_amount=total_amount)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders_for_user(db: Session, user_id: int) -> List[Order]:
    """
    Return all orders belonging to a given user_id (Integer).
    Used by the user account page and admin dashboard.
    """
    return db.query(Order).filter(Order.user_id == user_id).all()


def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
    order = get_order(db, order_id)
    if not order:
        return None
    order.status = status
    db.commit()
    db.refresh(order)
    return order


def get_order_summary(db: Session, user_id: int) -> dict:
    """Build a summary dict for a user's order history."""
    orders = get_orders_for_user(db, user_id)
    return {
        "user_id": user_id,  # Integer user_id passed through directly
        "total_orders": len(orders),
        "total_spent": sum(o.total_amount for o in orders),
    }
