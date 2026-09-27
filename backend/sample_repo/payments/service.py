"""
Payment service — handles payment processing.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sample_repo.models import Payment, Order, User


def create_payment(db: Session, user_id: int, order_id: int, amount: float, stripe_payment_id: str) -> Payment:
    """
    Record a payment. Validates that user_id and order_id exist.
    user_id is an Integer FK to users.id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    payment = Payment(
        user_id=user_id,
        order_id=order_id,
        amount=amount,
        stripe_payment_id=stripe_payment_id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payments_for_user(db: Session, user_id: int):
    """
    Retrieve all payment records for a user by Integer user_id.
    Exposed in the billing history endpoint.
    """
    return db.query(Payment).filter(Payment.user_id == user_id).all()


def refund_payment(db: Session, payment_id: int) -> Optional[Payment]:
    """Mark a payment as refunded."""
    payment = get_payment(db, payment_id)
    if not payment:
        return None
    payment.status = "refunded"
    db.commit()
    db.refresh(payment)
    return payment


def process_webhook(payload: dict) -> dict:
    """
    Handle Stripe webhook. Extracts user_id from payload metadata.
    metadata.user_id is currently stored as an Integer string.
    """
    user_id = int(payload.get("metadata", {}).get("user_id", 0))
    return {"user_id": user_id, "processed": True}
