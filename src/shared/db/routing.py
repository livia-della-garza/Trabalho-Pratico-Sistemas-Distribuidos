from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from shared.config import get_settings
from shared.db.session_factory import create_db_helpers


class Base(DeclarativeBase):
    pass


class RoutingLog(Base):
    __tablename__ = "routing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pergunta: Mapped[str] = mapped_column(Text, nullable=False)
    decisao: Mapped[str] = mapped_column(String(8), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


init_db, get_session = create_db_helpers(
    lambda: get_settings().routing_postgres_dsn,
    [RoutingLog],
)
