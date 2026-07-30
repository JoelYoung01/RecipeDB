"""Helpers for recipe body text (instructions, etc.)."""

from __future__ import annotations

import re

# Numbered step that starts a cooking instruction (e.g. "2. Add onions").
_STEP_BOUNDARY = re.compile(r"(?<=[.!?])[ \t]+(?=\d{1,2}\.\s+\S)")


def normalize_instruction_newlines(text: str) -> str:
    """Ensure numbered cooking steps are separated by newlines.

    Models often return a single paragraph like
    ``1. Heat oil. 2. Add onion. 3. Simmer.`` even when asked for \\n.
    We don't strip newlines — we only insert them when steps are mashed.
    """
    if not text:
        return text
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if "\n" in cleaned:
        return cleaned
    return _STEP_BOUNDARY.sub("\n", cleaned)
