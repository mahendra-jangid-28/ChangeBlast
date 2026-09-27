"""
Authentication and security utilities.
"""
import hashlib
import hmac
import secrets
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sample_repo.models import User, UserSession

SECRET_KEY = "dev-secret-key-change-in-production"
TOKEN_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    """Hash a plaintext password using SHA-256 + salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its stored hash."""
    salt, stored_hash = hashed.split(":", 1)
    check = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
    return hmac.compare_digest(check, stored_hash)


def create_session_token(db: Session, user_id: int) -> str:
    """
    Create an auth session for a user.
    Stores user_id (Integer) in user_sessions.user_id.
    """
    token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    )
    db.add(session)
    db.commit()
    return token


def get_user_from_token(db: Session, token: str) -> Optional[User]:
    """
    Validate a session token and return the associated User.
    Queries user_sessions by token, joins to users.id (Integer).
    This is the auth middleware used on every protected route.
    """
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session:
        return None
    if session.expires_at < datetime.utcnow():
        return None
    return db.query(User).filter(User.id == session.user_id).first()


def invalidate_token(db: Session, token: str) -> bool:
    """Logout — remove session token."""
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def build_user_jwt_payload(user: User) -> dict:
    """
    Build the JWT payload for a user.
    The 'sub' claim is user.id as a string (Integer cast to str).
    NOTE: If User.id changes to UUID, this payload format must also change.
    """
    return {
        "sub": str(user.id),   # Integer -> str here; JWT consumer parses back to int
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
