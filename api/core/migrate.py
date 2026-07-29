"""Apply Alembic migrations on process startup."""

from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def run_migrations() -> None:
    """Upgrade the configured SQLite database to Alembic head.

    Production keeps `data/` on a persistent volume across image deploys, so
    schema changes (e.g. password-auth columns) must be applied at boot —
    otherwise auth routes 500 with OperationalError and Google sign-in appears
    to do nothing in the SPA.
    """
    ini_path = _REPO_ROOT / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(_REPO_ROOT / "alembic"))
    logger.info("Running database migrations (%s)", ini_path)
    command.upgrade(cfg, "head")
    logger.info("Database migrations complete")
