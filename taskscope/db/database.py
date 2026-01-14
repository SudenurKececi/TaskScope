from __future__ import annotations

from pathlib import Path
from platformdirs import user_data_dir

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

APP_NAME = "TaskScope"
APP_AUTHOR = "TaskScope"


class Base(DeclarativeBase):
    pass


def get_db_path() -> Path:
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "taskscope.db"


DB_PATH = get_db_path()

DATABASE_URL = URL.create(
    "sqlite+pysqlite",
    database=str(DB_PATH),
)

ENGINE = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    # Model importu şart: tabloyu görsün
    from taskscope.models.task import Task  # noqa: F401
    Base.metadata.create_all(bind=ENGINE)
