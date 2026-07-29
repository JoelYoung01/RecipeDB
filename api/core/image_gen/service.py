"""High-level helpers for recipe cover generation / search."""

from __future__ import annotations

from typing import Any

from api.core.image_gen.client import ImageGenClient, get_image_gen_client
from api.core.image_gen.persist import save_cover_upload
from api.core.image_gen.prompts import build_recipe_image_prompt, recipe_image_keywords
from api.core.logging import logger
from api.models import Upload, User


def generate_recipe_cover_upload(
    *,
    user: User,
    db,
    title: str,
    description: str | None = None,
    ingredients: list[dict[str, Any]] | None = None,
    image_gen: ImageGenClient | None = None,
) -> Upload | None:
    """Run the configured provider and persist an Upload, or return None."""
    clean_title = (title or "").strip()
    if not clean_title:
        return None

    client = image_gen or get_image_gen_client()
    prompt = build_recipe_image_prompt(clean_title, description, ingredients)
    keywords = recipe_image_keywords(clean_title, ingredients)
    try:
        image = client.generate(
            prompt,
            recipe_title=clean_title,
            keywords=keywords,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Cover image provider failed for %r: %s", clean_title, exc)
        return None

    if image is None:
        return None

    upload = save_cover_upload(
        user=user,
        image=image,
        recipe_title=clean_title,
        db=db,
    )
    if upload is not None:
        logger.info(
            "Created cover upload %s for %r via %s",
            upload.id,
            clean_title,
            image.source,
        )
    return upload
