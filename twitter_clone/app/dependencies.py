from collections.abc import Generator

from .database import get_db


def get_db_session() -> Generator:
    yield from get_db()