"""User schema model."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from typing import Optional
from datetime import datetime
from typing_extensions import Annotated

from beanie import Document
from pydantic import BaseModel, EmailStr, Field

import src.utils.timer as t


class UserOut(BaseModel):
    """User out schema model."""

    username: str = Field(...)
    email: EmailStr = Field(...)


class User(Document):
    """User schema model for database."""

    username: str = Field(...,)
    email: EmailStr = Field(...)
    password: str = Field(...)
    is_active: bool = Field(...)
    is_superuser: bool = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    deleted_at: Optional[datetime] = Field(None)

    class Settings:
        name = "users"
        indexes = ["username", "email"]

    def to_out(self) -> UserOut:
        """Convert user object to out schema model."""
        return UserOut(username=self.username, email=self.email)


class UserRegister(BaseModel):
    """User registration schema model."""

    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "alfabeta",
                "email": "alfabeta@mail.com",
                "password": "superstrong",
            }
        }

    def to_user_schema(self) -> User:
        """Convert user registration object to user schema model."""
        return User(
            username=self.username,
            email=self.email,
            password=self.password,
            is_active=False,
            is_superuser=False,
            created_at=t.now(),
            updated_at=t.now(),
            deleted_at=None,
        )


class UserRegisterResponse(BaseModel):
    """User register response for API."""

    status: str = Field(...)
    message: str = Field(...)
    data: UserOut = Field(...)
    elapsed: float = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "User registered",
                "data": {
                    "username": "alfabeta",
                    "email": "alfabeta@mail.com",
                },
                "elapsed": 50.00,
            }
        }