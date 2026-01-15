"""
User repository.

Provides CRUD operations and helper methods
for the User entity in the database.
"""

from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.repositories.base import BaseRepository
from app.api.models.user import User
from app.api.models.portfolio import Portfolio


class UserRepository(BaseRepository):
    """
    Repository for managing User entities.

    Provides methods for fetching, creating, and updating
    users and their portfolios.
    """

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetches a user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User object if found, None otherwise.
        """
        return await self._db.get(User, user_id)

    async def get_by_id_with_portfolio(self, user_id: int) -> Optional[User]:
        """
        Fetches a user with their portfolio and assets (eager loading).

        Uses nested eager loading to avoid N+1 queries.

        Args:
            user_id: User identifier.

        Returns:
            User object with loaded portfolio and assets, or None.
        """
        query = (
            select(User)
            .options(
                selectinload(User.portfolio).selectinload(Portfolio.asset)
            )
            .where(User.id == user_id)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Fetches a user by username.

        Args:
            username: Username.

        Returns:
            User object if found, None otherwise.
        """
        query = select(User).where(User.username == username)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def update_balance(self, user: User, amount: Decimal) -> None:
        """
        Updates user's balance by the specified amount.

        Args:
            user: User object to update.
            amount: Amount to add (negative = subtract).
        """
        user.balance += amount

    async def get_all(self) -> List[User]:
        """
        Fetches all users.

        Returns:
            List of all users.
        """
        query = select(User)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Fetches a user by email address.

        Args:
            email: User's email address.

        Returns:
            User object if found, None otherwise.
        """
        query = select(User).where(User.email == email)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, username: str, email: str, hashed_password: str
    ) -> User:
        """
        Creates a new user.

        Args:
            username: Username.
            email: Email address.
            hashed_password: Hashed password.

        Returns:
            Created User object.
        """
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self._db.add(user)
        return user
