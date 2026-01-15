"""
Transaction repository.

Provides CRUD operations and helper methods
for the Transaction entity in the database.
"""

from decimal import Decimal
from typing import List

from sqlalchemy import select

from app.api.repositories.base import BaseRepository
from app.api.models.transaction import Transaction


class TransactionRepository(BaseRepository):
    """
    Repository for managing Transaction entities.

    Transaction represents a single buy or sell operation
    of an asset by a user.
    """

    async def create(
        self,
        user_id: int,
        asset_id: int,
        amount: Decimal,
        price: Decimal,
        transaction_type: str
    ) -> Transaction:
        """
        Creates a new transaction.

        Args:
            user_id: User identifier.
            asset_id: Asset identifier.
            amount: Amount of asset in the transaction.
            price: Asset price at the time of transaction.
            transaction_type: Transaction type ("BUY" or "SELL").

        Returns:
            Created Transaction object.
        """
        transaction = Transaction(
            user_id=user_id,
            asset_id=asset_id,
            amount=amount,
            price_at_transaction=price,
            type=transaction_type
        )
        self._db.add(transaction)
        return transaction

    async def get_user_transactions(
        self, user_id: int, limit: int = 50
    ) -> List[Transaction]:
        """
        Fetches user's transactions.

        Args:
            user_id: User identifier.
            limit: Maximum number of transactions to fetch.

        Returns:
            List of user's transactions.
        """
        query = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        """
        Fetches a transaction by ID.

        Args:
            transaction_id: Transaction identifier.

        Returns:
            Transaction object if found, None otherwise.
        """
        return await self._db.get(Transaction, transaction_id)

    async def get_by_user(self, user_id: int) -> List[Transaction]:
        """
        Fetches user's entire transaction history (for PnL calculations).
        Eagerly loads asset data.

        Args:
            user_id: User identifier.

        Returns:
            List of all user's transactions.
        """
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .options(selectinload(Transaction.asset))
            .order_by(Transaction.timestamp.asc())
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def delete_user_transactions(self, user_id: int) -> int:
        """
        Deletes all user's transactions.

        Args:
            user_id: User identifier.

        Returns:
            Number of deleted transactions.
        """
        from sqlalchemy import delete as sql_delete

        query = sql_delete(Transaction).where(Transaction.user_id == user_id)
        result = await self._db.execute(query)
        return result.rowcount

    async def delete_by_asset_id(self, asset_id: int) -> int:
        """
        Deletes all transactions for a specific asset.

        Args:
            asset_id: Asset identifier.

        Returns:
            Number of deleted transactions.
        """
        from sqlalchemy import delete as sql_delete

        query = sql_delete(Transaction).where(Transaction.asset_id == asset_id)
        result = await self._db.execute(query)
        return result.rowcount

