"""Pluggable cover-image providers for generated recipes."""

from api.core.image_gen.client import (
    ImageGenClient,
    ImageGenResult,
    get_image_gen_client,
)
from api.core.image_gen.prompts import build_recipe_image_prompt, recipe_image_keywords

__all__ = [
    "ImageGenClient",
    "ImageGenResult",
    "build_recipe_image_prompt",
    "get_image_gen_client",
    "recipe_image_keywords",
]
