"""Alembic helpers for deploy entrypoint and admin API."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import create_engine

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from api.core.config import settings

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def alembic_config() -> Config:
    ini_path = _REPO_ROOT / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "alembic"))
    return cfg


def current_revision() -> str | None:
    engine = create_engine(settings.SQLITE_DATABASE_URL)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()


def head_revision() -> str | None:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def run_migrations() -> dict[str, str | bool | None]:
    """Upgrade the configured SQLite database to Alembic head.

    Returns previous/current revisions so callers can report whether work ran.
    """
    before = current_revision()
    head = head_revision()
    logger.info("Running database migrations (from=%s head=%s)", before, head)
    command.upgrade(alembic_config(), "head")
    after = current_revision()
    logger.info("Database migrations complete (revision=%s)", after)
    return {
        "previous_revision": before,
        "current_revision": after,
        "head_revision": head,
        "upgraded": before != after,
    }
