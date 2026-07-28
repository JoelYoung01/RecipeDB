"""Aggregate planned-recipe ingredients into a grocery list."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from api.models import Ingredient, PlannedRecipe

CATEGORY_ORDER = [
    "Produce",
    "Meat & Seafood",
    "Dairy & Eggs",
    "Bakery",
    "Pantry",
    "Spices & Seasonings",
    "Frozen",
    "Beverages",
    "Other",
]

_CATEGORY_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    (
        "Produce",
        (
            "lettuce",
            "tomato",
            "onion",
            "garlic",
            "potato",
            "carrot",
            "celery",
            "cucumber",
            "bell pepper",
            "avocado",
            "lemon",
            "lime",
            "apple",
            "banana",
            "berry",
            "blueberry",
            "strawberry",
            "spinach",
            "kale",
            "broccoli",
            "cabbage",
            "zucchini",
            "mushroom",
            "cilantro",
            "parsley",
            "basil",
            "ginger",
            "scallion",
            "shallot",
            "jalapeño",
            "jalapeno",
        ),
    ),
    (
        "Meat & Seafood",
        (
            "chicken",
            "beef",
            "pork",
            "bacon",
            "sausage",
            "turkey",
            "ham",
            "steak",
            "ground beef",
            "pancetta",
            "fish",
            "salmon",
            "shrimp",
            "tuna",
            "seafood",
        ),
    ),
    (
        "Dairy & Eggs",
        (
            "milk",
            "butter",
            "cheese",
            "feta",
            "parmesan",
            "cream",
            "yogurt",
            "egg",
            "sour cream",
            "mozzarella",
            "cheddar",
        ),
    ),
    (
        "Bakery",
        (
            "bread",
            "tortilla",
            "taco shell",
            "bun",
            "roll",
            "bagel",
            "pita",
            "noodle",
            "pasta",
            "spaghetti",
        ),
    ),
    (
        "Spices & Seasonings",
        (
            "salt",
            "pepper",
            "spice",
            "seasoning",
            "cumin",
            "paprika",
            "oregano",
            "cinnamon",
            "vanilla",
            "chili powder",
            "taco seasoning",
            "bay leaf",
            "thyme",
            "rosemary",
        ),
    ),
    (
        "Frozen",
        ("frozen", "ice cream"),
    ),
    (
        "Beverages",
        ("juice", "wine", "beer", "coffee", "tea", "soda"),
    ),
    (
        "Pantry",
        (
            "flour",
            "sugar",
            "oil",
            "olive oil",
            "vinegar",
            "soy sauce",
            "rice",
            "bean",
            "sauce",
            "honey",
            "syrup",
            "baking",
            "chocolate",
            "oat",
            "broth",
            "stock",
            "tomato paste",
            "coconut",
            "peanut",
        ),
    ),
]


def normalize_item_key(name: str) -> str:
    key = name.strip().lower()
    return re.sub(r"\s+", " ", key)


def infer_category(name: str) -> str:
    lowered = name.lower()
    for category, keywords in _CATEGORY_KEYWORDS:
        for keyword in keywords:
            if keyword in lowered:
                return category
    return "Other"


def format_amount(amount: float | None) -> str | None:
    if amount is None:
        return None
    if float(amount).is_integer():
        return str(int(amount))
    return f"{amount:.2f}".rstrip("0").rstrip(".")


def format_quantity(amount: float | None, units: str | None) -> str | None:
    amount_text = format_amount(amount)
    unit_text = (units or "").strip()
    if amount_text and unit_text:
        return f"{amount_text} {unit_text}"
    if amount_text:
        return amount_text
    if unit_text:
        return unit_text
    return None


def aggregate_grocery_items(planned: list[PlannedRecipe]) -> list[dict]:
    """Collapse ingredients across planned recipes by normalized name."""
    buckets: dict[str, dict] = {}

    for plan in planned:
        recipe = plan.recipe
        if recipe is None:
            continue
        ingredients: list[Ingredient] = list(recipe.ingredients or [])
        for ingredient in ingredients:
            key = normalize_item_key(ingredient.name)
            if not key:
                continue

            bucket = buckets.get(key)
            if bucket is None:
                bucket = {
                    "key": key,
                    "name": ingredient.name.strip(),
                    "category": infer_category(ingredient.name),
                    # unit_key -> {total, saw_amount}
                    "by_unit": {},
                    "unit_order": [],
                    "recipes": {},
                    "source_ingredient_ids": [],
                }
                buckets[key] = bucket

            unit_key = (ingredient.units or "").strip().lower()
            display_unit = (ingredient.units or "").strip() or None
            if unit_key not in bucket["by_unit"]:
                bucket["unit_order"].append(unit_key)
                bucket["by_unit"][unit_key] = {
                    "total": 0.0,
                    "saw_amount": False,
                    "display_unit": display_unit,
                }
            entry = bucket["by_unit"][unit_key]
            if entry["display_unit"] is None and display_unit:
                entry["display_unit"] = display_unit
            if ingredient.amount is not None:
                entry["total"] += float(ingredient.amount)
                entry["saw_amount"] = True

            if recipe.id not in bucket["recipes"]:
                bucket["recipes"][recipe.id] = recipe.name
            bucket["source_ingredient_ids"].append(ingredient.id)

    items: list[dict] = []
    for bucket in buckets.values():
        quantities: list[dict] = []
        quantity_parts: list[str] = []

        for unit_key in bucket["unit_order"]:
            entry = bucket["by_unit"][unit_key]
            amount = entry["total"] if entry["saw_amount"] else None
            units = entry["display_unit"]
            quantities.append({"amount": amount, "units": units})
            part = format_quantity(amount, units)
            if part:
                quantity_parts.append(part)

        recipes = [
            {"id": rid, "name": rname}
            for rid, rname in sorted(
                bucket["recipes"].items(), key=lambda x: x[1].lower()
            )
        ]
        items.append(
            {
                "key": bucket["key"],
                "name": bucket["name"],
                "category": bucket["category"],
                "quantities": quantities,
                "quantity_display": ", ".join(quantity_parts),
                "recipes": recipes,
                "recipe_titles": ", ".join(r["name"] for r in recipes),
                "source_ingredient_ids": bucket["source_ingredient_ids"],
            }
        )

    def sort_key(item: dict) -> tuple:
        try:
            cat_idx = CATEGORY_ORDER.index(item["category"])
        except ValueError:
            cat_idx = len(CATEGORY_ORDER)
        return (cat_idx, item["name"].lower())

    items.sort(key=sort_key)
    return items


def window_bounds(now: datetime) -> tuple[datetime, datetime]:
    """Return [start_of_today, end_of_day + 6 days] for the sliding 7-day window."""
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6)
    end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end
