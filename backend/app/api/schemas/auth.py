from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    """
    Input data for user registration.

    Attributes:
        username: Unique username (3-50 characters).
        email: User's email address.
        password: Password (minimum 6 characters).
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """
    Input data for login.

    Attributes:
        username: Username.
        password: Password.
    """

    username: str
    password: str


class Token(BaseModel):
    """
    Response containing the JWT token.

    Attributes:
        access_token: JWT access token.
        token_type: Token type (always "bearer").
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Data decoded from the JWT token.

    Attributes:
        user_id: User ID extracted from the token.
    """

    user_id: int | None = None


class UserResponse(BaseModel):
    """
    User data returned by the API.

    Attributes:
        id: User identifier.
        username: Username.
        email: Email address.
        balance: USD balance.
        role: User role.
        is_active: Whether the account is active.
    """

    id: int
    username: str
    email: str
    balance: Decimal
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)