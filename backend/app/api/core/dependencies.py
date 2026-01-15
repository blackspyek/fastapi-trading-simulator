from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.repositories import (
    UserRepository,
    AssetRepository,
    PortfolioRepository,
    TransactionRepository,
    PriceHistoryRepository,
)
from app.api.services.trade_service import TradeService

def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    """
    Provides a UserRepository instance.

    Args:
        db: Database session injected by FastAPI.

    Returns:
        UserRepository instance with connected session.
    """
    return UserRepository(db)


def get_asset_repository(
    db: AsyncSession = Depends(get_db)
) -> AssetRepository:
    """
    Provides an AssetRepository instance.

    Args:
        db: Database session injected by FastAPI.

    Returns:
        AssetRepository instance with connected session.
    """
    return AssetRepository(db)


def get_portfolio_repository(
    db: AsyncSession = Depends(get_db)
) -> PortfolioRepository:
    """
    Provides a PortfolioRepository instance.

    Args:
        db: Database session injected by FastAPI.

    Returns:
        PortfolioRepository instance with connected session.
    """
    return PortfolioRepository(db)


def get_transaction_repository(
    db: AsyncSession = Depends(get_db)
) -> TransactionRepository:
    """
    Provides a TransactionRepository instance.

    Args:
        db: Database session injected by FastAPI.

    Returns:
        TransactionRepository instance with connected session.
    """
    return TransactionRepository(db)


def get_price_history_repository(
    db: AsyncSession = Depends(get_db)
) -> PriceHistoryRepository:
    """
    Provides a PriceHistoryRepository instance.

    Args:
        db: Database session injected by FastAPI.

    Returns:
        PriceHistoryRepository instance with connected session.
    """
    return PriceHistoryRepository(db)


def get_trade_service(
    user_repo: UserRepository = Depends(get_user_repository),
    asset_repo: AssetRepository = Depends(get_asset_repository),
    portfolio_repo: PortfolioRepository = Depends(get_portfolio_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    db: AsyncSession = Depends(get_db)
) -> TradeService:
    """
    Provides a TradeService instance with injected repositories.

    Args:
        user_repo: User repository.
        asset_repo: Asset repository.
        portfolio_repo: Portfolio repository.
        transaction_repo: Transaction repository.
        db: Database session (for commit/rollback).

    Returns:
        Configured TradeService instance.
    """
    return TradeService(
        user_repo=user_repo,
        asset_repo=asset_repo,
        portfolio_repo=portfolio_repo,
        transaction_repo=transaction_repo,
        db=db
    )


from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from app.api.core.security import decode_token
from app.api.services.auth_service import AuthService
from app.api.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_db)
) -> AuthService:
    """
    Provides an AuthService instance.

    Args:
        user_repo: User repository.
        db: Database session.

    Returns:
        Configured AuthService instance.
    """
    return AuthService(user_repo=user_repo, db=db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Retrieves the current user from JWT token.

    Args:
        token: JWT token from Authorization header.
        user_repo: User repository.

    Returns:
        User object of the currently logged-in user.

    Raises:
        HTTPException: 401 if token is invalid or user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user

from app.api.models.user import UserRole
from app.api.services.asset_service import AssetService


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Requires administrator privileges.

    Args:
        current_user: Currently logged-in user.

    Returns:
        User object if user is an administrator.

    Raises:
        HTTPException: 403 if user is not an administrator.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required."
        )
    return current_user


from app.api.clients.binance_client import BinanceClient

def get_asset_service(
    asset_repo: AssetRepository = Depends(get_asset_repository),
    portfolio_repo: PortfolioRepository = Depends(get_portfolio_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
    db: AsyncSession = Depends(get_db)
) -> AssetService:
    """
    Provides an AssetService instance.

    Args:
        asset_repo: Asset repository.
        portfolio_repo: Portfolio repository.
        transaction_repo: Transaction repository.
        price_history_repo: Price history repository.
        db: Database session.

    Returns:
        Configured AssetService instance.
    """
    binance_client = BinanceClient()
    
    return AssetService(
        asset_repo=asset_repo,
        portfolio_repo=portfolio_repo,
        transaction_repo=transaction_repo,
        price_history_repo=price_history_repo,
        db=db,
        binance_client=binance_client
    )


