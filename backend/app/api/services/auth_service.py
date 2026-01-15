from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.user import User
from app.api.repositories.user_repository import UserRepository
from app.api.schemas.auth import UserRegister, Token
from app.api.core.security import hash_password, verify_password, create_access_token


class AuthService:
    """
    Service handling user registration and authentication.

    Attributes:
        _user_repo: User repository.
        _db: Database session for commit/rollback.
    """

    def __init__(self, user_repo: UserRepository, db: AsyncSession) -> None:
        """
        Initializes the service with required dependencies.

        Args:
            user_repo: User repository.
            db: Database session.
        """
        self._user_repo: UserRepository = user_repo
        self._db: AsyncSession = db

    async def register(self, data: UserRegister) -> User:
        """
        Registers a new user.

        Args:
            data: Registration data (username, email, password).

        Returns:
            Created User object.

        Raises:
            HTTPException: 400 if username or email already exists.
        """
        existing_user = await self._user_repo.get_by_username(data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this username already exists."
            )

        existing_email = await self._user_repo.get_by_email(data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )

        hashed = hash_password(data.password)
        user = await self._user_repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hashed
        )

        await self._db.commit()
        await self._db.refresh(user)

        return user

    async def authenticate(self, username: str, password: str) -> Token:
        """
        Authenticates a user and returns a JWT token.

        Args:
            username: Username.
            password: Password.

        Returns:
            Token object with access_token.

        Raises:
            HTTPException: 401 if login credentials are invalid.
        """
        user = await self._user_repo.get_by_username(username)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive."
            )

        access_token = create_access_token(data={"sub": str(user.id)})

        return Token(access_token=access_token)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetches a user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User object or None.
        """
        return await self._user_repo.get_by_id(user_id)
