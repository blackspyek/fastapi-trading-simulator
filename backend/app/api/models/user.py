"""
User model.

Represents a user in the cryptocurrency trading system.
"""

from decimal import Decimal
from enum import Enum
from typing import List

from sqlalchemy import String, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.db.base import Base


class UserRole(str, Enum):
    """
    User roles in the system.

    Attributes:
        ADMIN: Administrator with full management access.
        USER: Regular user with trading access.
    """

    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    System user model.

    Attributes:
        id: Unique user identifier.
        username: Unique username.
        email: Unique email address.
        hashed_password: Hashed password (bcrypt).
        balance: User's USD balance.
        role: User role (ADMIN or USER).
        is_active: Whether the account is active.
        transactions: List of user's transactions.
        portfolio: List of user's portfolio positions.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=100000.00)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")
    portfolio: Mapped[List["Portfolio"]] = relationship(back_populates="user")