import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.api.db.session import AsyncSessionLocal
from app.api.models.asset import Asset
from app.api.models.user import User, UserRole
from app.api.core.security import hash_password
from decimal import Decimal

async def seed():
    async with AsyncSessionLocal() as db:
        if not await db.get(User, 1):
            db.add(User(
                username="admin",
                email="admin@tradingsim.com",
                hashed_password=hash_password("admin123"),
                balance=Decimal("100000.00"),
                role=UserRole.ADMIN.value,
                is_active=True
            ))

            assets_data = [
                {"ticker": "BTC", "name": "Bitcoin", "binance_symbol": "BTCUSDT", "current_price": 40000.00},
                {"ticker": "ETH", "name": "Ethereum", "binance_symbol": "ETHUSDT", "current_price": 2200.00},
                {"ticker": "SOL", "name": "Solana", "binance_symbol": "SOLUSDT", "current_price": 90.00},
            ]

            for data in assets_data:
                db.add(Asset(**data))

            await db.commit()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())