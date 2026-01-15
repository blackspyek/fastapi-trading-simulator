from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import jwt, JWTError

from app.api.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against its hashed version.

    Args:
        plain_password: The password in plain text.
        hashed_password: The hashed password from the database.

    Returns:
        True if passwords match, False otherwise.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password: The password to hash.

    Returns:
        The hashed password string.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(
    data: dict[str, Any],
    expires_after: Optional[timedelta] = None
) -> str:
    """
    Creates a JWT access token.

    Args:
        data: Data to encode in the token (e.g., user_id).
        expires_after: Token expiration time. Defaults to configuration settings.

    Returns:
        Encoded JWT token as a string.
    """
    to_encode = data.copy()
    
    if expires_after:
        expire = datetime.now(timezone.utc) + expires_after
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decodes and validates a JWT token.

    Args:
        token: The JWT token to decode.

    Returns:
        Dictionary with token payload if valid, None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None