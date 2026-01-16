from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    Base repository class providing database session access.

    All repositories should inherit from this class
    to have unified access to the SQLAlchemy session.

    Attributes:
        _db: Async SQLAlchemy session for database operations.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initializes the repository with a database session.

        Args:
            db: Async SQLAlchemy session.
        """
        self._db: AsyncSession = db
