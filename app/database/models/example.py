"""Example database models for demonstration purposes."""

from datetime import datetime

from sqlalchemy import Integer, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class ConnectionHistory(Base):
    """SSH connection history record."""

    __tablename__ = "connection_history"

    id: Mapped[int] = mapped_column(Integer, Sequence("connection_history_id_seq"), primary_key=True)
    host: Mapped[str] = mapped_column(nullable=False)
    user: Mapped[str] = mapped_column(nullable=False)
    port: Mapped[int] = mapped_column(default=22)
    connected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status: Mapped[str] = mapped_column(nullable=False)
    error_message: Mapped[str | None] = mapped_column(nullable=True)
