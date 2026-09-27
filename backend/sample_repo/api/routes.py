"""
REST API routes for the e-commerce platform.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from sample_repo.models import User, Order, Payment
from sample_repo.users.service import get_user_by_id, create_user, list_users, delete_user
from sample_repo.users.schemas import UserCreate, UserResponse, UserListResponse
from sample_repo.orders.service import create_order, get_order, get_orders_for_user
from sample_repo.payments.service import get_payments_for_user, refund_payment
from sample_repo.auth.security import create_session_token, get_user_from_token

router = APIRouter()


# ---- User endpoints ----

@router.get("/users", response_model=UserListResponse, tags=["users"])
def list_all_users(db: Session = Depends(None)):
    """Return a paginated list of all users. Admin only."""
    users = list_users(db)
    return {"users": users, "total": len(users)}


@router.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
def get_user(user_id: int, db: Session = Depends(None)):
    """
    Fetch a user by Integer ID.
    Path param user_id must be int — changing User.id to UUID breaks this route.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserResponse, status_code=201, tags=["users"])
def create_new_user(payload: UserCreate, db: Session = Depends(None)):
    """Create a new user account."""
    return create_user(db, payload.email, payload.password, payload.full_name)


@router.delete("/users/{user_id}", status_code=204, tags=["users"])
def remove_user(user_id: int, db: Session = Depends(None)):
    """Delete a user by Integer ID. Cascades to orders/payments."""
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")


# ---- Order endpoints ----

@router.get("/users/{user_id}/orders", tags=["orders"])
def get_user_orders(user_id: int, db: Session = Depends(None)):
    """
    Fetch all orders for a user by Integer user_id.
    This endpoint exposes user_id as an integer in the URL.
    """
    orders = get_orders_for_user(db, user_id)
    return {"user_id": user_id, "orders": orders}


@router.post("/orders", status_code=201, tags=["orders"])
def place_order(user_id: int, total_amount: float, db: Session = Depends(None)):
    """Place an order. user_id is the Integer PK of the user."""
    try:
        order = create_order(db, user_id, total_amount)
        return order
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/orders/{order_id}", tags=["orders"])
def fetch_order(order_id: int, db: Session = Depends(None)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ---- Payment endpoints ----

@router.get("/users/{user_id}/payments", tags=["payments"])
def get_user_payments(user_id: int, db: Session = Depends(None)):
    """
    Return payment history for a user.
    user_id is an Integer in the URL path.
    """
    return get_payments_for_user(db, user_id)


@router.post("/payments/{payment_id}/refund", tags=["payments"])
def process_refund(payment_id: int, db: Session = Depends(None)):
    """Initiate a refund for a payment."""
    payment = refund_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"status": "refunded", "payment_id": payment_id}


# ---- Auth endpoints ----

@router.post("/auth/login", tags=["auth"])
def login(email: str, password: str, db: Session = Depends(None)):
    """
    Authenticate user and issue session token.
    Creates entry in user_sessions with user_id (Integer FK).
    """
    from sample_repo.users.service import authenticate_user
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session_token(db, user.id)
    return {"token": token, "user_id": user.id}  # user.id returned as Integer


@router.post("/auth/logout", tags=["auth"])
def logout(token: str, db: Session = Depends(None)):
    """Invalidate a session token."""
    from sample_repo.auth.security import invalidate_token
    invalidate_token(db, token)
    return {"status": "logged_out"}
