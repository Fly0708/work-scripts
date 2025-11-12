import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

# Global engine instance for singleton pattern
_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def get_database_path() -> Path:
    """Get the database file path, in the same directory as config files.

    Returns:
        Path: Path to the database file (work_scripts.db)
    """
    if os.name == "nt":
        config_dir = Path(os.getenv("APPDATA")) / "work_scripts"
    else:
        config_dir = Path.home() / ".config" / "work_scripts"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "work_scripts.db"


def get_engine() -> Engine:
    """Create and return SQLAlchemy engine (singleton pattern).

    Returns:
        Engine: SQLAlchemy engine instance connected to DuckDB
    """
    global _engine

    if _engine is None:
        db_path = get_database_path()
        connection_string = f"duckdb:///{db_path}"
        _engine = create_engine(connection_string, echo=False)

    return _engine


def get_session_factory() -> sessionmaker:
    """Return session factory for creating database sessions.

    Returns:
        sessionmaker: SQLAlchemy session factory
    """
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    return _session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions with automatic commit and rollback.

    Yields:
        Session: SQLAlchemy session instance

    Example:
        with get_session() as session:
            repo = SomeRepository(session)
            repo.create(entity)
    """
    factory = get_session_factory()
    session = factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    """Initialize database and create all tables.

    This function should be called during application startup to ensure
    all database tables are created.

    Raises:
        RuntimeError: If database initialization fails
    """
    try:
        from .base import Base

        engine = get_engine()
        Base.metadata.create_all(engine)

        db_path = get_database_path()
        print(f"Database initialized at {db_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize database: {e}") from e
