from collections.abc import Callable, Generator, Sequence
from typing import TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


def create_db_helpers(
    dsn_getter: Callable[[], str],
    models: Sequence[type[DeclarativeBase]],
) -> tuple[Callable[[], None], Callable[[], Generator[Session, None, None]]]:
    engine = None
    session_local = None

    def _ensure_engine() -> None:
        nonlocal engine, session_local
        if engine is None:
            engine = create_engine(dsn_getter(), pool_pre_ping=True)
            session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def init_db() -> None:
        _ensure_engine()
        for model in models:
            model.metadata.create_all(bind=engine)

    def get_session() -> Generator[Session, None, None]:
        _ensure_engine()
        session = session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return init_db, get_session
