"""Database module for work-scripts application.

This module provides database integration using SQLAlchemy and DuckDB.
"""

from .base import Base, BaseRepository
from .config import get_session, init_database
from .models.example import ConnectionHistory
from .repositories.example_repository import ConnectionHistoryRepository