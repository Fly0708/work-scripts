"""Repository implementation for ConnectionHistory model."""

from sqlalchemy import select

from ..base import BaseRepository
from ..models.example import ConnectionHistory


class ConnectionHistoryRepository(BaseRepository[ConnectionHistory]):
    """Repository for managing SSH connection history records.

    Provides specialized query methods for connection history data
    in addition to the standard CRUD operations from BaseRepository.
    """

    def __init__(self, session) -> None:
        """Initialize the repository with a session.

        Args:
            session: SQLAlchemy session for database operations
        """
        super().__init__(session, ConnectionHistory)

    def get_recent_connections(self, limit: int = 10) -> list[ConnectionHistory]:
        """Get the most recent connection records.

        Args:
            limit: Maximum number of records to return (default: 10)

        Returns:
            list[ConnectionHistory]: List of recent connections ordered by time (newest first)
        """
        stmt = select(ConnectionHistory).order_by(ConnectionHistory.connected_at.desc()).limit(limit)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_host(self, host: str) -> list[ConnectionHistory]:
        """Get all connection records for a specific host.

        Args:
            host: The hostname to filter by

        Returns:
            list[ConnectionHistory]: List of connections to the specified host
        """
        return self.find(host=host)

    def get_successful_connections(self) -> list[ConnectionHistory]:
        """Get all successful connection records.

        Returns:
            list[ConnectionHistory]: List of connections with status "success"
        """
        return self.find(status="success")
