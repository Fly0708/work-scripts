from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Session

# Type variable for generic repository
T = TypeVar("T", bound="Base")


class Base(DeclarativeBase):
    """Declarative base class for all database models.

    All model classes should inherit from this base class to be
    registered with SQLAlchemy's ORM system.
    """

    pass


class BaseRepository(Generic[T]):
    """Generic base repository class providing common CRUD operations.

    This class provides standard database operations for any model type.
    Subclasses can extend this with model-specific query methods.

    Type Parameters:
        T: The model class type this repository manages

    Attributes:
        session: SQLAlchemy session for database operations
        model: The model class this repository manages
    """

    def __init__(self, session: Session, model: Type[T]) -> None:
        """Initialize the repository with a session and model class.

        Args:
            session: SQLAlchemy session for database operations
            model: The model class this repository manages
        """
        self.session = session
        self.model = model

    def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: The entity instance to create

        Returns:
            T: The created entity with updated fields (e.g., generated ID)
        """
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, id: Any) -> T | None:
        """Get an entity by its primary key ID.

        Args:
            id: The primary key value to search for

        Returns:
            T | None: The entity if found, None otherwise
        """
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        """Get all entities of this model type.

        Returns:
            list[T]: List of all entities
        """
        stmt = select(self.model)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update(self, entity: T) -> T:
        """Update an existing entity in the database.

        Args:
            entity: The entity instance to update

        Returns:
            T: The updated entity
        """
        self.session.merge(entity)
        self.session.flush()
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity from the database.

        Args:
            entity: The entity instance to delete
        """
        self.session.delete(entity)
        self.session.flush()

    def find(self, **filters) -> list[T]:
        """Find entities matching the given filters.

        Args:
            **filters: Keyword arguments representing field=value filters

        Returns:
            list[T]: List of entities matching all filters

        Example:
            repo.find(status="active", user="john")
        """
        stmt = select(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        result = self.session.execute(stmt)
        return list(result.scalars().all())
