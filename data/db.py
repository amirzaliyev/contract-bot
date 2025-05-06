from __future__ import annotations
from typing import TYPE_CHECKING, Type
from uuid import uuid4

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from config import settings


if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL
    from data.models import Base
    from sqlalchemy.orm import Session

def get_engine(url: URL | str = settings.database_url) -> Engine:
    return create_engine(
        url=url,
        echo=settings.DEBUG
    )


def get_sessionmaker(engine: Engine) -> 'sessionmaker[Session]':
    return sessionmaker(engine)

def init_db(engine: Engine, base: Type[Base]):
    base.metadata.create_all(engine)


db_url = settings.database_url_psycopg2
engine = get_engine(url=db_url)
sessionmaker_factory = get_sessionmaker(engine)

