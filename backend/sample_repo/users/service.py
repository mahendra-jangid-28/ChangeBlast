"""
User service — business logic for user management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sample_repo.models import User
from sample_repo.auth.security import hash_password, verify_password


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a single user by their Integer ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a user by email address."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Return a paginated list of users."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, email: str, password: str, full_name: str) -> User:
    """Create and persist a new user."""
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user fields by user_id (Integer)."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    for field, value in kwargs.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user record. Cascades to orders and payments."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email/password. Used in login flow."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
