from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, LargeBinary, Integer, DateTime, Index

from app.db.base import Base


class Checkpoint(Base):
    """
    Модель для хранения чекпоинтов LangGraph.

    Таблица: checkpoints
    Позволяет восстанавливать состояние графа после сбоев.
    """
    __tablename__ = "checkpoints"

    # Первичный ключ
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Идентификатор сессии (thread_id в LangGraph)
    thread_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Идентификатор чекпоинта (уникален в рамках thread_id)
    checkpoint_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Идентификатор родительского чекпоинта (для ветвления)
    parent_checkpoint_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Сериализованное состояние графа (JSON или pickle)
    checkpoint_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    # Метаданные чекпоинта (например, версия схемы)
    checkpoint_metadata: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # Время создания
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Уникальный индекс: один чекпоинт на thread_id + checkpoint_id
    __table_args__ = (
        Index("ix_checkpoints_thread_checkpoint", "thread_id", "checkpoint_id", unique=True),
        Index("ix_checkpoints_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f""