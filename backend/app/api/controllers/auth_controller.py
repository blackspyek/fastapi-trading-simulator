from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from app.api.core.dependencies import get_auth_service, get_current_user
from app.api.services.auth_service import AuthService
from app.api.models.user import User
from app.api.schemas.auth import UserRegister, UserLogin, UserResponse, Token

router = APIRouter()


@cbv(router)
class AuthController:
    """
    REST API controller for authentication operations.

    Handles new user registration, login,
    and fetching currently logged-in user data.

    Attributes:
        auth_service: Injected authentication service.
    """

    auth_service: AuthService = Depends(get_auth_service)

    @router.post("/register", response_model=UserResponse, status_code=201)
    async def register(self, data: UserRegister) -> UserResponse:
        """
        Registers a new user.

        Args:
            data: Registration data (username, email, password).

        Returns:
            Created user data.

        Raises:
            HTTPException: 400 if username or email already exists.
        """
        user = await self.auth_service.register(data)
        return UserResponse.model_validate(user)

    @router.post("/login", response_model=Token)
    async def login(self, data: UserLogin) -> Token:
        """
        Logs in a user and returns a JWT token.

        Args:
            data: Login data as JSON (username, password).

        Returns:
            JWT token for authorizing subsequent requests.

        Raises:
            HTTPException: 401 if login credentials are invalid.
        """
        return await self.auth_service.authenticate(
            username=data.username,
            password=data.password
        )

    @router.get("/me", response_model=UserResponse)
    async def get_me(
        self, current_user: User = Depends(get_current_user)
    ) -> UserResponse:
        """
        Fetches currently logged-in user data.

        Args:
            current_user: User decoded from JWT token.

        Returns:
            Current user data.
        """
        return UserResponse.model_validate(current_user)
