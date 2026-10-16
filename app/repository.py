
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgres://"))

_pg_pool = None

def backend() -> str:
    return "postgresql" if IS_POSTGRES else "sqlite"

def configure_postgres_pool() -> None:
    global _pg_pool
    if not IS_POSTGRES or _pg_pool is not None:
        return
    try:
        from psycopg_pool import ConnectionPool
    except ImportError as exc:
        raise RuntimeError("PostgreSQL backend selected but psycopg_pool is not installed") from exc
    _pg_pool = ConnectionPool(
        conninfo=DATABASE_URL,
        min_size=int(os.getenv("PG_POOL_MIN", "1")),
        max_size=int(os.getenv("PG_POOL_MAX", "10")),
        open=True,
        kwargs={"autocommit": False},
    )

@contextmanager
def transaction(db_path: str | None = None) -> Iterator[Any]:
    """
    Production transaction boundary.
    PostgreSQL is selected with DATABASE_URL.
    SQLite remains the local MVP fallback.
    """
    if IS_POSTGRES:
        configure_postgres_pool()
        with _pg_pool.connection() as c:
            try:
                yield c
                c.commit()
            except Exception:
                c.rollback()
                raise
        return

    if not db_path:
        raise ValueError("db_path required for sqlite transaction")
    c = sqlite3.connect(db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        c.execute("BEGIN")
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

def as_dict(row: Any) -> dict[str, Any] | None:
    if row is None:
        return None
    try:
        return dict(row)
    except TypeError:
        return dict(row)
