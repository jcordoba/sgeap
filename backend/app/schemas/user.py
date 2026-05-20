"""User schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a user."""
    email: EmailStr
    password: str
    nombre_completo: Optional[str] = None
    role_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    nombre_completo: Optional[str]
    activo: bool
    role_id: Optional[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data extracted from JWT."""
    user_id: Optional[str] = None
    email: Optional[str] = None