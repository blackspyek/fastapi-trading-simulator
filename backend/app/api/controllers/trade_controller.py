from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from app.api.core.dependencies import get_trade_service, get_current_user
from app.api.services.trade_service import TradeService
from app.api.models.user import User
from app.api.schemas.trade import TradeRequest, TransactionResponse

router = APIRouter()


@cbv(router)
class TradeController:
    """
    REST API controller for trading operations.

    Handles buy, sell, and wallet status endpoints.
    All endpoints require JWT authorization.

    Attributes:
        trade_service: Injected trading service.
        current_user: Currently logged-in user.
    """

    trade_service: TradeService = Depends(get_trade_service)
    current_user: User = Depends(get_current_user)

    @router.post("/buy", response_model=TransactionResponse)
    async def buy_asset(self, trade_data: TradeRequest) -> TransactionResponse:
        """
        Buys cryptocurrency for USD.

        Args:
            trade_data: Transaction data (ticker, amount).

        Returns:
            Details of the executed buy transaction.

        Raises:
            HTTPException: 404 if asset doesn't exist.
            HTTPException: 400 if insufficient funds.
        """
        return await self.trade_service.execute_trade(
            user_id=self.current_user.id,
            trade_data=trade_data,
            trade_type="BUY"
        )

    @router.post("/sell", response_model=TransactionResponse)
    async def sell_asset(self, trade_data: TradeRequest) -> TransactionResponse:
        """
        Sells owned cryptocurrency for USD.

        Args:
            trade_data: Transaction data (ticker, amount).

        Returns:
            Details of the executed sell transaction.

        Raises:
            HTTPException: 404 if asset doesn't exist.
            HTTPException: 400 if insufficient asset quantity.
        """
        return await self.trade_service.execute_trade(
            user_id=self.current_user.id,
            trade_data=trade_data,
            trade_type="SELL"
        )

    @router.get("/wallet")
    async def get_wallet_status(self) -> dict:
        """
        Fetches currently logged-in user's wallet status.

        Returns:
            Dictionary with username, USD balance, and list of owned assets.
        """
        return await self.trade_service.get_wallet(self.current_user.id)

    @router.post("/reset-account")
    async def reset_account(self) -> dict:
        """
        Resets user account to initial state.

        Deletes entire portfolio, all transactions, and restores balance
        to initial value ($100,000).

        Returns:
            Dictionary with reset information.
        """
        return await self.trade_service.reset_account(self.current_user.id)
