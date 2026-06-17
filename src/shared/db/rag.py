from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from shared.config import get_settings
from shared.db.session_factory import create_db_helpers


class Base(DeclarativeBase):
    pass


class RagInteraction(Base):
    __tablename__ = "rag_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)
    chunks_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


init_db, get_session = create_db_helpers(
    lambda: get_settings().rag_postgres_dsn,
    [RagInteraction],
)
