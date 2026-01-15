from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.api.models.user import User
from app.api.schemas.trade import TradeRequest, TransactionResponse
from app.api.services.trade_service import TradeService

router = APIRouter()

HARDCODED_USER_ID = 1

@router.post("/buy", response_model=TransactionResponse)
async def buy_asset(
    trade_data: TradeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Kupuje kryptowalutę (np. BTC) za USD.

    :returns TransactionResponse: Szczegóły wykonanej transakcji kupna.
    """
    return await TradeService.execute_trade(
        db=db,
        user_id=HARDCODED_USER_ID,
        trade_data=trade_data,
        trade_type="BUY"
    )

@router.post("/sell", response_model=TransactionResponse)
async def sell_asset(
    trade_data: TradeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sprzedaje posiadaną kryptowalutę i otrzymuje USD.

    :returns TransactionResponse: Szczegóły wykonanej transakcji sprzedaży.
    """
    return await TradeService.execute_trade(
        db=db,
        user_id=HARDCODED_USER_ID,
        trade_data=trade_data,
        trade_type="SELL"
    )

@router.get("/wallet")
async def get_wallet_status(db: AsyncSession = Depends(get_db)):
    """
    Pomocniczy endpoint: Zwraca saldo USD i posiadane krypto.
    Przydatne, żeby sprawdzić czy transakcja zadziałała.
    """
    # Pobieramy usera wraz z jego portfolio (eager loading)
    query = select(User).options(selectinload(User.portfolio)).where(User.id == HARDCODED_USER_ID)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    portfolio_list = [
        {
            "asset_id": p.asset_id,
            "quantity": float(p.quantity)
        }
        for p in user.portfolio
    ]

    return {
        "username": user.username,
        "usd_balance": float(user.balance),
        "portfolio": portfolio_list
    }