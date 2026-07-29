"""Persist generated/fetched cover bytes as Upload rows."""

from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime
from pathlib import Path

from api.core.config import settings
from api.core.image_gen.client import ImageGenResult
from api.core.logging import logger
from api.models import Upload, User


def save_cover_upload(
    *,
    user: User,
    image: ImageGenResult,
    recipe_title: str,
    db,
) -> Upload | None:
    """Write image bytes under UPLOAD_DIR and return a committed Upload row."""
    upload_root = Path(settings.UPLOAD_DIR)
    user_dir = upload_root / str(user.id)
    try:
        user_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.error("Could not create upload dir %s: %s", user_dir, exc)
        return None

    slug = _slugify(recipe_title) or "recipe"
    file_hash = secrets.token_hex(8)
    file_name = f"{slug}_cover_{file_hash}.{image.extension}"
    rel_path = Path(str(user.id)) / file_name
    full_path = upload_root / rel_path

    try:
        full_path.write_bytes(image.content)
    except OSError as exc:
        logger.error("Failed writing cover image to %s: %s", full_path, exc)
        return None

    display_name = f"{slug}_cover.{image.extension}"
    if image.attribution:
        # Keep attribution discoverable without a schema change.
        display_name = f"{display_name} — {image.attribution[:180]}"

    db_file = Upload(
        created_by_id=user.id,
        created_on=datetime.now(UTC),
        file_path=str(rel_path),
        name=display_name[:255],
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower())
    return cleaned.strip("-")[:48]
