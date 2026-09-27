"""
Pydantic schemas for the Users API.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[int] = None


class UserResponse(UserBase):
    id: int           # Currently Integer — target of migration to UUID
    is_active: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
