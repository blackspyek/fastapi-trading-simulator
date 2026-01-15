from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.api.models.user import User
from app.api.models.asset import Asset
from app.api.models.transaction import Transaction
from app.api.models.portfolio import Portfolio
from app.api.schemas.trade import TradeRequest
from app.api.repositories import (
    UserRepository,
    AssetRepository,
    PortfolioRepository,
    TransactionRepository,
)


class TradeService:
    """
    Service implementing trading business logic.

    Responsible for executing buy and sell transactions,
    validating funds, and updating user portfolio.

    Attributes:
        _user_repo: User repository.
        _asset_repo: Asset repository.
        _portfolio_repo: Portfolio repository.
        _transaction_repo: Transaction repository.
        _db: Database session for commit/rollback.
    """

    # Constant for initial balance
    INITIAL_BALANCE = Decimal("100000.00")

    def __init__(
        self,
        user_repo: UserRepository,
        asset_repo: AssetRepository,
        portfolio_repo: PortfolioRepository,
        transaction_repo: TransactionRepository,
        db: AsyncSession
    ) -> None:
        """
        Initializes the service with required repositories.

        Args:
            user_repo: User repository.
            asset_repo: Asset repository.
            portfolio_repo: Portfolio repository.
            transaction_repo: Transaction repository.
            db: Database session for transaction management.
        """
        self._user_repo: UserRepository = user_repo
        self._asset_repo: AssetRepository = asset_repo
        self._portfolio_repo: PortfolioRepository = portfolio_repo
        self._transaction_repo: TransactionRepository = transaction_repo
        self._db: AsyncSession = db

    async def execute_trade(
        self,
        user_id: int,
        trade_data: TradeRequest,
        trade_type: str
    ) -> Transaction:
        """
        Executes a trade transaction (buy or sell).

        Args:
            user_id: Identifier of the user executing the transaction.
            trade_data: Transaction data (ticker, amount).
            trade_type: Transaction type ("BUY" or "SELL").

        Returns:
            Created Transaction object with transaction data.

        Raises:
            HTTPException: 404 if user or asset doesn't exist.
            HTTPException: 400 if insufficient funds or invalid type.
        """
        user, asset = await self._get_valid_resources(user_id, trade_data.asset_ticker)
        portfolio_item = await self._portfolio_repo.get_by_user_and_asset(
            user_id, asset.id
        )

        total_value: Decimal = asset.current_price * trade_data.amount

        if trade_type == "BUY":
            await self._process_buy(user, asset, portfolio_item, trade_data.amount, total_value)
        elif trade_type == "SELL":
            self._process_sell(user, asset, portfolio_item, trade_data.amount, total_value)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction type (expected BUY/SELL)."
            )

        transaction = await self._transaction_repo.create(
            user_id=user.id,
            asset_id=asset.id,
            amount=trade_data.amount,
            price=asset.current_price,
            transaction_type=trade_type
        )

        await self._db.commit()
        await self._db.refresh(transaction)

        transaction.ticker = asset.ticker
        return transaction

    async def get_wallet(self, user_id: int) -> Dict[str, Any]:
        """
        Fetches user's wallet status.

        Args:
            user_id: User identifier.

        Returns:
            Dictionary with USD balance and list of owned assets with full data.

        Raises:
            HTTPException: 404 if user doesn't exist.
        """
        # Uses nested eager loading - single query with JOIN instead of N+1
        user = await self._user_repo.get_by_id_with_portfolio(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        assets_list: List[Dict[str, Any]] = []
        total_assets_value: Decimal = Decimal(0)

        # Fetch transaction history to calculate average buy price
        transactions = await self._transaction_repo.get_by_user(user_id)
        
        # Map: asset_ticker -> { 'total_cost': Decimal, 'quantity': Decimal, 'avg_price': Decimal }
        asset_stats = {}

        # Sort transactions from oldest to properly reconstruct history
        transactions.sort(key=lambda x: x.timestamp)

        for tx in transactions:
            ticker = tx.asset.ticker
            if ticker not in asset_stats:
                asset_stats[ticker] = {'total_cost': Decimal(0), 'quantity': Decimal(0), 'avg_price': Decimal(0)}
            
            stats = asset_stats[ticker]
            
            if tx.type == "BUY":
                # Increase quantity and total cost
                stats['quantity'] += tx.amount
                stats['total_cost'] += tx.amount * tx.price_at_transaction
                
                # Update average price (weighted average)
                if stats['quantity'] > 0:
                    stats['avg_price'] = stats['total_cost'] / stats['quantity']
                
            elif tx.type == "SELL":
                # Decrease quantity and cost proportionally to average price
                # (assuming we sell "averaged" units, which doesn't change the average buy price of remaining)
                stats['quantity'] -= tx.amount
                stats['total_cost'] -= tx.amount * stats['avg_price']
                
                # If we sold everything, reset (or leave at 0)
                if stats['quantity'] <= 0:
                    stats['quantity'] = Decimal(0)
                    stats['total_cost'] = Decimal(0)
                    stats['avg_price'] = Decimal(0)

        # Build assets list
        assets_list: List[Dict[str, Any]] = []
        total_assets_value: Decimal = Decimal(0)

        # Portfolio and Asset are already loaded via selectinload
        for p in user.portfolio:
            asset = p.asset  # Already loaded - no additional query!
            if asset:
                value = p.quantity * asset.current_price
                total_assets_value += value
                
                # Get calculated average price
                avg_price = Decimal(0)
                if asset.ticker in asset_stats:
                    avg_price = asset_stats[asset.ticker]['avg_price']

                assets_list.append({
                    "ticker": asset.ticker,
                    "name": asset.name,
                    "amount": float(p.quantity),
                    "current_price": float(asset.current_price),
                    "value": float(value),
                    "average_buy_price": float(avg_price),
                    "is_active": asset.is_active
                })

        return {
            "username": user.username,
            "balance": float(user.balance),
            "assets": assets_list,
            "total_value": float(user.balance + total_assets_value)
        }

    async def _get_valid_resources(
        self, user_id: int, ticker: str
    ) -> Tuple[User, Asset]:
        """
        Fetches and validates user and asset.

        Args:
            user_id: User identifier.
            ticker: Asset symbol.

        Returns:
            Tuple (User, Asset) if both exist.

        Raises:
            HTTPException: 404 if user or asset doesn't exist.
        """
        user = await self._user_repo.get_by_id(user_id)
        asset = await self._asset_repo.get_by_ticker(ticker)

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset '{ticker}' doesn't exist.")

        return user, asset

    async def _process_buy(
        self,
        user: User,
        asset: Asset,
        portfolio_item: Optional[Portfolio],
        amount: Decimal,
        cost: Decimal
    ) -> None:
        """
        Processes a buy transaction.

        Checks balance, deducts funds, and adds asset to portfolio.

        Args:
            user: User making the purchase.
            asset: Asset being purchased.
            portfolio_item: Existing portfolio entry (if exists).
            amount: Amount to purchase.
            cost: Total transaction cost.

        Raises:
            HTTPException: 400 if insufficient funds.
        """
        if user.balance < cost:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. You have {user.balance:.2f}, need {cost:.2f}"
            )

        await self._user_repo.update_balance(user, -cost)

        if portfolio_item:
            await self._portfolio_repo.update_quantity(portfolio_item, amount)
        else:
            await self._portfolio_repo.create(user.id, asset.id, amount)

    def _process_sell(
        self,
        user: User,
        asset: Asset,
        portfolio_item: Optional[Portfolio],
        amount: Decimal,
        income: Decimal
    ) -> None:
        """
        Processes a sell transaction.

        Checks owned assets, adds funds, and deducts from portfolio.

        Args:
            user: User making the sale.
            asset: Asset being sold.
            portfolio_item: Portfolio entry (must exist).
            amount: Amount to sell.
            income: Transaction income.

        Raises:
            HTTPException: 400 if insufficient asset quantity.
        """
        if not portfolio_item or portfolio_item.quantity < amount:
            owned = portfolio_item.quantity if portfolio_item else Decimal(0)
            raise HTTPException(
                status_code=400,
                detail=f"You don't have enough {asset.ticker}. You own: {owned}"
            )

        user.balance += income
        portfolio_item.quantity -= amount

    async def reset_account(self, user_id: int) -> Dict[str, Any]:
        """
        Resets user account to initial state.

        Deletes entire portfolio, all transactions, and restores balance
        to initial value ($100,000).

        Args:
            user_id: User identifier.

        Returns:
            Dictionary with reset information (deleted items, new balance).

        Raises:
            HTTPException: 404 if user doesn't exist.
        """
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        deleted_portfolio = await self._portfolio_repo.delete_user_portfolio(user_id)

        deleted_transactions = await self._transaction_repo.delete_user_transactions(user_id)

        user.balance = self.INITIAL_BALANCE

        await self._db.commit()

        return {
            "success": True,
            "message": "Account has been reset successfully.",
            "deleted_portfolio_items": deleted_portfolio,
            "deleted_transactions": deleted_transactions,
            "new_balance": float(self.INITIAL_BALANCE)
        }
