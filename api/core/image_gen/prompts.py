"""Shared prompt / search-query builders for recipe cover images."""

from __future__ import annotations

from typing import Any

# Low-signal tokens we never want as the sole search anchor.
_SKIP_INGREDIENTS = {
    "salt",
    "pepper",
    "water",
    "oil",
    "olive oil",
    "vegetable oil",
    "black pepper",
    "kosher salt",
    "butter",
    "garlic",
    "onion",
    "sugar",
    "flour",
}


def recipe_image_keywords(
    title: str,
    ingredients: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Concrete food nouns for search ranking (ingredients first, then title words)."""
    names: list[str] = []
    for ing in ingredients or []:
        name = str(ing.get("name") or "").strip().lower()
        if not name or name in _SKIP_INGREDIENTS:
            continue
        if name not in names:
            names.append(name)
        if len(names) >= 4:
            break

    # Pull a couple of content words from the title if ingredients are sparse.
    if len(names) < 2:
        stop = {
            "with",
            "and",
            "the",
            "over",
            "a",
            "in",
            "of",
            "for",
            "sheet-pan",
            "sheet",
            "pan",
            "one-skillet",
            "skillet",
            "weeknight",
            "stubbed",
            "bowl",
            "style",
        }
        for token in (title or "").lower().replace(",", " ").split():
            token = token.strip("-")
            if len(token) < 4 or token in stop or token in names:
                continue
            names.append(token)
            if len(names) >= 4:
                break
    return names


def build_recipe_image_prompt(
    title: str,
    description: str | None = None,
    ingredients: list[dict[str, Any]] | None = None,
) -> str:
    """Build a short food-photo query from recipe fields.

    Used as a diffusion prompt later, and as an Openverse search query for the
    broke adapter. Keep it concrete and food-focused.
    """
    keywords = recipe_image_keywords(title, ingredients)
    clean_title = (title or "").strip()

    # Prefer a compact ingredient-led query — Openverse hates long phrases.
    if keywords:
        return f"{' '.join(keywords[:3])} dinner plated food"

    if clean_title:
        return f"{clean_title} dinner plated food"

    desc = (description or "").strip()
    if desc:
        return f"{desc.split('.')[0].strip()[:80]} food"

    return "homemade dinner plated food"
