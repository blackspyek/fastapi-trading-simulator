import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.services.trade_service import TradeService
from app.api.schemas.trade import TradeRequest
from app.api.models.user import User
from app.api.models.asset import Asset
from app.api.models.portfolio import Portfolio
from app.api.models.transaction import Transaction


class TestTradeServiceExecuteTradeBuy:
    """Tests for execute_trade method (BUY)."""

    @pytest.mark.asyncio
    async def test_given_sufficient_funds_when_buy_then_transaction_created(self) -> None:
        """Sufficient funds -> execute_trade BUY -> transaction created."""
        user = MagicMock(spec=User)
        user.id = 1
        user.balance = Decimal("10000")
        
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        asset.current_price = Decimal("100")
        
        transaction = MagicMock(spec=Transaction)
        transaction.id = 1
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = asset
        
        portfolio_repo = AsyncMock()
        portfolio_repo.get_by_user_and_asset.return_value = None
        
        transaction_repo = AsyncMock()
        transaction_repo.create.return_value = transaction
        
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="BUY")
        
        user_repo.update_balance.assert_called_once()
        portfolio_repo.create.assert_called_once()
        transaction_repo.create.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_insufficient_funds_when_buy_then_exception_raised(self) -> None:
        """Insufficient funds -> execute_trade BUY -> HTTPException 400."""
        user = MagicMock(spec=User)
        user.id = 1
        user.balance = Decimal("50")
        
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        asset.current_price = Decimal("100")
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = asset
        
        portfolio_repo = AsyncMock()
        portfolio_repo.get_by_user_and_asset.return_value = None
        
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        with pytest.raises(HTTPException) as exc_info:
            await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="BUY")
        
        assert exc_info.value.status_code == 400
        transaction_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_user_not_found_when_buy_then_exception_raised(self) -> None:
        """User not found -> execute_trade -> HTTPException 404."""
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = None
        
        asset_repo = AsyncMock()
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        with pytest.raises(HTTPException) as exc_info:
            await service.execute_trade(user_id=999, trade_data=trade_data, trade_type="BUY")
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_given_asset_not_found_when_buy_then_exception_raised(self) -> None:
        """Asset not found -> execute_trade -> HTTPException 404."""
        user = MagicMock(spec=User)
        user.id = 1
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = None
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="INVALID", amount=Decimal("1"))
        
        with pytest.raises(HTTPException) as exc_info:
            await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="BUY")
        
        assert exc_info.value.status_code == 404


class TestTradeServiceExecuteTradeSell:
    """Tests for execute_trade method (SELL)."""

    @pytest.mark.asyncio
    async def test_given_owned_asset_when_sell_then_transaction_created(self) -> None:
        """Owned asset -> execute_trade SELL -> transaction created."""
        user = MagicMock(spec=User)
        user.id = 1
        user.balance = Decimal("1000")
        
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        asset.current_price = Decimal("100")
        
        portfolio = MagicMock(spec=Portfolio)
        portfolio.quantity = Decimal("5")
        
        transaction = MagicMock(spec=Transaction)
        transaction.id = 1
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = asset
        
        portfolio_repo = AsyncMock()
        portfolio_repo.get_by_user_and_asset.return_value = portfolio
        
        transaction_repo = AsyncMock()
        transaction_repo.create.return_value = transaction
        
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="SELL")
        
        transaction_repo.create.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_insufficient_quantity_when_sell_then_exception_raised(self) -> None:
        """Insufficient quantity -> execute_trade SELL -> HTTPException 400."""
        user = MagicMock(spec=User)
        user.id = 1
        
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        asset.current_price = Decimal("100")
        
        portfolio = MagicMock(spec=Portfolio)
        portfolio.quantity = Decimal("0.5")  # Not enough
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = asset
        
        portfolio_repo = AsyncMock()
        portfolio_repo.get_by_user_and_asset.return_value = portfolio
        
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        with pytest.raises(HTTPException) as exc_info:
            await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="SELL")
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_given_no_portfolio_when_sell_then_exception_raised(self) -> None:
        """No portfolio -> execute_trade SELL -> HTTPException 400."""
        user = MagicMock(spec=User)
        user.id = 1
        
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        asset.current_price = Decimal("100")
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = asset
        
        portfolio_repo = AsyncMock()
        portfolio_repo.get_by_user_and_asset.return_value = None  # None
        
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        trade_data = TradeRequest(asset_ticker="BTC", amount=Decimal("1"))
        
        with pytest.raises(HTTPException) as exc_info:
            await service.execute_trade(user_id=1, trade_data=trade_data, trade_type="SELL")
        
        assert exc_info.value.status_code == 400


class TestTradeServiceGetWallet:
    """Tests for get_wallet method."""

    @pytest.mark.asyncio
    async def test_given_user_exists_when_get_wallet_then_wallet_returned(self) -> None:
        """User exists -> get_wallet -> wallet data."""
        user = MagicMock(spec=User)
        user.username = "testuser"
        user.balance = Decimal("5000")
        user.portfolio = []
        
        user_repo = AsyncMock()
        user_repo.get_by_id_with_portfolio.return_value = user
        
        asset_repo = AsyncMock()
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        transaction_repo.get_by_user.return_value = []
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        result = await service.get_wallet(user_id=1)
        
        # Assert
        assert result["username"] == "testuser"
        assert result["balance"] == 5000.0

    @pytest.mark.asyncio
    async def test_given_user_not_found_when_get_wallet_then_exception_raised(self) -> None:
        """User not found -> get_wallet -> HTTPException 404."""
        user_repo = AsyncMock()
        user_repo.get_by_id_with_portfolio.return_value = None
        
        asset_repo = AsyncMock()
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_wallet(user_id=999)
        
        assert exc_info.value.status_code == 404


class TestTradeServiceResetAccount:
    """Tests for reset_account method."""

    @pytest.mark.asyncio
    async def test_given_user_exists_when_reset_account_then_portfolio_cleared_and_balance_reset(self) -> None:
        """User exists -> reset_account -> portfolio/transactions cleared, balance reset."""
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.balance = Decimal("5000")
        
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = user
        
        asset_repo = AsyncMock()
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        result = await service.reset_account(user_id=1)
        
        assert result["message"] == "Account has been reset successfully."
        assert result["new_balance"] == 100000.0
        
        portfolio_repo.delete_user_portfolio.assert_called_once_with(1)
        transaction_repo.delete_user_transactions.assert_called_once_with(1)
        
        assert user.balance == Decimal("100000.00")
        db.commit.assert_called_once()
        user_repo.update_balance.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_user_not_found_when_reset_account_then_exception_raised(self) -> None:
        """User not found -> reset_account -> HTTPException 404."""
        user_repo = AsyncMock()
        user_repo.get_by_id.return_value = None
        
        asset_repo = AsyncMock()
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        db = AsyncMock()
        
        service = TradeService(
            user_repo=user_repo,
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            db=db
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await service.reset_account(user_id=999)
        
        assert exc_info.value.status_code == 404
