import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.api.services.auth_service import AuthService
from app.api.schemas.auth import UserRegister
from app.api.models.user import User, UserRole


class TestAuthServiceRegister:
    """Tests for the register method."""

    @pytest.mark.asyncio
    async def test_given_valid_data_when_register_then_user_created(self) -> None:
        """Valid data -> register -> user created."""
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = None
        user_repo.get_by_email.return_value = None
        
        new_user = MagicMock(spec=User)
        new_user.id = 1
        new_user.username = "newuser"
        new_user.email = "new@example.com"
        user_repo.create.return_value = new_user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        data = UserRegister(username="newuser", email="new@example.com", password="password123")
        
        result = await service.register(data)
        
        assert result.username == "newuser"
        user_repo.get_by_username.assert_called_once_with("newuser")
        user_repo.get_by_email.assert_called_once_with("new@example.com")
        user_repo.create.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_existing_username_when_register_then_exception_raised(self) -> None:
        """Existing username -> register -> HTTPException 400."""
        existing_user = MagicMock(spec=User)
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = existing_user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        data = UserRegister(username="existing", email="new@example.com", password="password123")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.register(data)
        
        assert exc_info.value.status_code == 400
        user_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_existing_email_when_register_then_exception_raised(self) -> None:
        """Existing email -> register -> HTTPException 400."""
        existing_user = MagicMock(spec=User)
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = None
        user_repo.get_by_email.return_value = existing_user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        data = UserRegister(username="newuser", email="existing@example.com", password="password123")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.register(data)
        
        assert exc_info.value.status_code == 400
        user_repo.create.assert_not_called()


class TestAuthServiceAuthenticate:
    """Tests for the authenticate method."""

    @pytest.mark.asyncio
    async def test_given_valid_credentials_when_authenticate_then_token_returned(self) -> None:
        """Valid credentials -> authenticate -> JWT token."""
        from app.api.core.security import hash_password
        
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.hashed_password = hash_password("password123")
        user.is_active = True
        
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        token = await service.authenticate("testuser", "password123")
        
        assert token.access_token is not None
        assert token.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_given_wrong_password_when_authenticate_then_exception_raised(self) -> None:
        """Wrong password -> authenticate -> HTTPException 401."""
        from app.api.core.security import hash_password
        
        user = MagicMock(spec=User)
        user.hashed_password = hash_password("correctpassword")
        user.is_active = True
        
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate("testuser", "wrongpassword")
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_given_nonexistent_user_when_authenticate_then_exception_raised(self) -> None:
        """Non-existent user -> authenticate -> HTTPException 401."""
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = None
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate("nonexistent", "password123")
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_given_inactive_user_when_authenticate_then_exception_raised(self) -> None:
        """Inactive user -> authenticate -> HTTPException 403."""
        from app.api.core.security import hash_password
        
        user = MagicMock(spec=User)
        user.hashed_password = hash_password("password123")
        user.is_active = False
        
        user_repo = AsyncMock()
        user_repo.get_by_username.return_value = user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate("testuser", "password123")
        
        assert exc_info.value.status_code == 403


class TestAuthServiceGetUserById:
    """Tests for get_user_by_id method."""

    @pytest.mark.asyncio
    async def test_given_user_exists_when_get_user_by_id_then_user_returned(self) -> None:
        """User exists -> get_user_by_id -> user returned."""
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "testuser"
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        result = await service.get_user_by_id(1)
        
        assert result is not None
        assert result.username == "testuser"
        user_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_given_user_not_exists_when_get_user_by_id_then_none_returned(self) -> None:
        """User doesn't exist -> get_user_by_id -> None."""
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = None
        
        db = AsyncMock()
        service = AuthService(user_repo=user_repo, db=db)
        
        result = await service.get_user_by_id(999)
        
        assert result is None
        user_repo.get_by_id.assert_called_once_with(999)

