from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from shared.config import get_settings
from shared.db.session_factory import create_db_helpers


class Base(DeclarativeBase):
    pass


class FimInteraction(Base):
    __tablename__ = "fim_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    resposta: Mapped[str] = mapped_column(Text, nullable=False)
    template_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


init_db, get_session = create_db_helpers(
    lambda: get_settings().fallback_postgres_dsn,
    [FimInteraction],
)
