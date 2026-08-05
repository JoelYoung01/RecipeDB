"""Parse free-text recipe ingredient lines into structured fields."""

from __future__ import annotations

import re
from typing import Any

# Common culinary units (singular + plural / abbreviations).
_UNITS = (
    r"teaspoons?",
    r"tablespoons?",
    r"tsp\.?",
    r"tbsp\.?",
    r"tbs\.?",
    r"cups?",
    r"c\.?",
    r"ounces?",
    r"oz\.?",
    r"pounds?",
    r"lbs?\.?",
    r"grams?",
    r"kilograms?",
    r"g\.?",
    r"kg\.?",
    r"milliliters?",
    r"liters?",
    r"ml\.?",
    r"l\.?",
    r"fluid ounces?",
    r"fl\.?\s*oz\.?",
    r"pints?",
    r"quarts?",
    r"gallons?",
    r"cloves?",
    r"slices?",
    r"pieces?",
    r"pinches?",
    r"dashes?",
    r"cans?",
    r"packages?",
    r"pkg\.?",
    r"bunches?",
    r"heads?",
    r"stalks?",
    r"sprigs?",
    r"leaves?",
    r"sheets?",
    r"sticks?",
    r"cubes?",
    r"handfuls?",
    r"large",
    r"medium",
    r"small",
)

_UNIT_RE = "|".join(_UNITS)

# 1, 1/2, 1½, 1 1/2, 2.5, .5, 1-2
_AMOUNT_RE = (
    r"(?P<amount>"
    r"\d+\s+\d+\s*/\s*\d+"  # 1 1/2
    r"|\d+\s*/\s*\d+"  # 1/2
    r"|\d*[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]"  # unicode fractions / mixed
    r"|\d+(?:\.\d+)?"  # 2 or 2.5
    r"|\.\d+"  # .5
    r"|\d+\s*-\s*\d+"  # 2-3
    r")"
)

_LINE_RE = re.compile(
    rf"^\s*{_AMOUNT_RE}" rf"(?:\s*(?P<units>{_UNIT_RE}))?" rf"(?:\s+(?P<rest>.+))?$",
    re.IGNORECASE,
)

_UNICODE_FRACTIONS = {
    "½": 0.5,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "¼": 0.25,
    "¾": 0.75,
    "⅕": 0.2,
    "⅖": 0.4,
    "⅗": 0.6,
    "⅘": 0.8,
    "⅙": 1 / 6,
    "⅚": 5 / 6,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
}

# Normalize unit display to short forms when obvious.
_UNIT_NORMALIZE = {
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    "tsp.": "tsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "tbsp.": "tbsp",
    "tbs": "tbsp",
    "tbs.": "tbsp",
    "cup": "cup",
    "cups": "cups",
    "c.": "cup",
    "ounce": "oz",
    "ounces": "oz",
    "oz.": "oz",
    "pound": "lb",
    "pounds": "lb",
    "lb.": "lb",
    "lbs": "lb",
    "lbs.": "lb",
    "gram": "g",
    "grams": "g",
    "g.": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "kg.": "kg",
    "milliliter": "ml",
    "milliliters": "ml",
    "ml.": "ml",
    "liter": "l",
    "liters": "l",
    "l.": "l",
    "clove": "cloves",
    "cloves": "cloves",
    "package": "package",
    "packages": "packages",
    "pkg.": "package",
    "pkg": "package",
}


def parse_amount(raw: str) -> float | None:
    """Convert a quantity token to float. Ranges use the lower bound."""
    text = (raw or "").strip().lower().replace(" ", "")
    if not text:
        return None

    # Range like 2-3 → take first
    if "-" in text and "/" not in text:
        text = text.split("-", 1)[0]

    # Mixed unicode: 1½
    if len(text) >= 2 and text[-1] in _UNICODE_FRACTIONS and text[:-1].isdigit():
        return float(text[:-1]) + _UNICODE_FRACTIONS[text[-1]]

    if text in _UNICODE_FRACTIONS:
        return _UNICODE_FRACTIONS[text]

    # Mixed ascii: 1 1/2 (spaces already stripped → 11/2 is wrong). Re-parse original.
    spaced = (raw or "").strip()
    mixed = re.match(r"^(\d+)\s+(\d+)\s*/\s*(\d+)$", spaced)
    if mixed:
        whole, num, den = mixed.groups()
        den_f = float(den)
        if den_f == 0:
            return None
        return float(whole) + float(num) / den_f

    frac = re.match(r"^(\d+)\s*/\s*(\d+)$", spaced)
    if frac:
        num, den = frac.groups()
        den_f = float(den)
        if den_f == 0:
            return None
        return float(num) / den_f

    try:
        return float(text)
    except ValueError:
        return None


def _split_name_details(rest: str) -> tuple[str, str | None]:
    text = rest.strip().strip(",").strip()
    if not text:
        return "ingredient", None

    # Parenthetical details: "flour (sifted)" or leading "(14 oz) can tomatoes"
    # Prefer trailing comma / em-dash style: "garlic, minced"
    for sep in (",", " - ", " – ", " — "):
        if sep in text:
            name, details = text.split(sep, 1)
            name = name.strip()
            details = details.strip().strip(",").strip()
            if name and details:
                return name, details

    paren = re.match(r"^(?P<name>.+?)\s*\((?P<details>[^)]+)\)\s*$", text)
    if paren:
        name = paren.group("name").strip()
        details = paren.group("details").strip()
        if name and details:
            return name, details

    return text, None


def parse_ingredient_line(line: str) -> dict[str, Any]:
    """Parse one ingredient line into name / amount / units / details."""
    cleaned = re.sub(r"\s+", " ", (line or "").strip())
    cleaned = cleaned.lstrip("-•*").strip()
    if not cleaned:
        return {
            "name": "ingredient",
            "amount": None,
            "units": None,
            "details": None,
        }

    match = _LINE_RE.match(cleaned)
    if not match:
        name, details = _split_name_details(cleaned)
        return {
            "name": name[:200],
            "amount": None,
            "units": None,
            "details": details[:200] if details else None,
        }

    amount = parse_amount(match.group("amount") or "")
    units_raw = (match.group("units") or "").strip()
    units = _UNIT_NORMALIZE.get(units_raw.lower(), units_raw or None)
    if units == "":
        units = None

    rest = (match.group("rest") or "").strip()
    if not rest:
        # e.g. "2 cups" with no ingredient name — unusual, keep raw line
        return {
            "name": cleaned[:200],
            "amount": amount,
            "units": units,
            "details": None,
        }

    # Leading parenthetical size: "1 (14 oz) can diced tomatoes"
    leading_paren = re.match(
        r"^\((?P<details>[^)]+)\)\s+(?P<rest>.+)$",
        rest,
    )
    if leading_paren:
        size_detail = leading_paren.group("details").strip()
        after = leading_paren.group("rest").strip()
        container = re.match(
            r"^(?P<container>cans?|packages?|jars?|bottles?|boxes?|bags?|pkg\.?)\s+"
            r"(?P<name>.+)$",
            after,
            re.IGNORECASE,
        )
        if container and not units:
            name, details = _split_name_details(container.group("name"))
            cont = container.group("container").rstrip(".").lower()
            if cont.startswith("pkg"):
                cont = "package"
            merged = size_detail if not details else f"{size_detail}; {details}"
            return {
                "name": name[:200],
                "amount": amount,
                "units": cont,
                "details": merged[:200],
            }
        name, details = _split_name_details(after)
        merged = size_detail if not details else f"{size_detail}; {details}"
        return {
            "name": name[:200],
            "amount": amount,
            "units": units,
            "details": merged[:200],
        }

    name, details = _split_name_details(rest)
    return {
        "name": name[:200],
        "amount": amount,
        "units": units,
        "details": details[:200] if details else None,
    }
