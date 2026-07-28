"""OpenRouter-ready LLM client. Uses a deterministic stub until credentials exist."""

from __future__ import annotations

import hashlib
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from api.core.config import settings


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class LlmTurnResult:
    """Normalized result from one LLM turn (ideation or build)."""

    content: str
    parsed: Any = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    stubbed: bool = True


class LlmClient(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
    ) -> LlmTurnResult:
        raise NotImplementedError


class StubLlmClient(LlmClient):
    """Pseudo-random but seedable responses so the pipeline stays testable."""

    PROTEINS = [
        "chicken",
        "salmon",
        "tofu",
        "black bean",
        "turkey",
        "shrimp",
        "lentil",
        "pork",
        "chickpea",
        "beef",
    ]
    STYLES = [
        "sheet-pan",
        "one-skillet",
        "stir-fry",
        "grain bowl",
        "tacos",
        "curry",
        "pasta",
        "salad",
        "soup",
        "roast",
    ]
    TWISTS = [
        "with lemon herb glaze",
        "and roasted veggies",
        "over brown rice",
        "with chili-lime dressing",
        "and crispy garlic",
        "in a coconut broth",
        "with tahini drizzle",
        "and quick pickled onions",
        "with miso butter",
        "and charred broccoli",
    ]

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
    ) -> LlmTurnResult:
        seed_src = "|".join(f"{m.role}:{m.content}" for m in messages)
        seed = int(hashlib.sha256(seed_src.encode()).hexdigest()[:16], 16)
        rng = random.Random(seed)

        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        mode = "build" if "BUILD_RECIPES" in last_user else "ideate"
        if mode == "ideate":
            count = self._extract_count(last_user, default=8)
            ideas = [self._idea(rng, i) for i in range(count)]
            return LlmTurnResult(
                content=f"Generated {count} stub ideas",
                parsed={"ideas": ideas},
                stubbed=True,
            )

        titles = self._extract_titles(last_user)
        recipes = [self._recipe(rng, title) for title in titles]
        return LlmTurnResult(
            content=f"Built {len(recipes)} stub recipes",
            parsed={"recipes": recipes},
            stubbed=True,
        )

    def _extract_count(self, text: str, default: int) -> int:
        marker = "IDEATE_COUNT="
        if marker in text:
            try:
                return max(1, int(text.split(marker, 1)[1].split()[0]))
            except (ValueError, IndexError):
                return default
        return default

    def _extract_titles(self, text: str) -> list[str]:
        titles: list[str] = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("- "):
                titles.append(line[2:].strip())
        return titles or ["Stubbed Weeknight Bowl"]

    def _idea(self, rng: random.Random, index: int) -> dict[str, str]:
        protein = rng.choice(self.PROTEINS)
        style = rng.choice(self.STYLES)
        twist = rng.choice(self.TWISTS)
        title = f"{protein.title()} {style.title()} {twist}"
        justification = (
            f"Fits your preferences with a {protein}-forward {style} that stays "
            "weeknight-friendly while keeping variety across the plan "
            f"(option {index + 1})."
        )
        return {"title": title, "justification": justification}

    def _recipe(self, rng: random.Random, title: str) -> dict[str, Any]:
        protein = next(
            (p for p in self.PROTEINS if p in title.lower()), rng.choice(self.PROTEINS)
        )
        prep = rng.choice([20, 25, 30, 35, 40, 45])
        ingredients = [
            {"name": protein, "amount": 1.0, "units": "lb", "details": "main protein"},
            {
                "name": "olive oil",
                "amount": 2.0,
                "units": "tbsp",
                "details": None,
            },
            {
                "name": "garlic",
                "amount": 3.0,
                "units": "cloves",
                "details": "minced",
            },
            {
                "name": rng.choice(
                    ["broccoli", "spinach", "bell pepper", "zucchini", "kale"]
                ),
                "amount": 2.0,
                "units": "cups",
                "details": "chopped",
            },
            {
                "name": rng.choice(["rice", "quinoa", "pasta", "potatoes"]),
                "amount": 1.0,
                "units": "cup",
                "details": "dry",
            },
            {
                "name": "salt",
                "amount": None,
                "units": None,
                "details": "to taste",
            },
        ]
        instructions = (
            f"1. Prep the {protein} and vegetables.\n"
            f"2. Heat oil in a pan; cook aromatics until fragrant.\n"
            f"3. Add {protein} and cook through.\n"
            f"4. Fold in vegetables and finish with seasoning.\n"
            f"5. Serve hot. (Stub recipe — replace with OpenRouter output later.)"
        )
        return {
            "title": title,
            "description": f"A stubbed weeknight dinner centered on {protein}.",
            "instructions": instructions,
            "notes": "Generated by stub LLM. Not a real tested recipe.",
            "prep_time": float(prep),
            "ingredients": ingredients,
            "source": "generated",
            "existing_recipe_id": None,
        }


class OpenRouterLlmClient(LlmClient):
    """Placeholder for real OpenRouter calls once credentials are available."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
    ) -> LlmTurnResult:
        # Intentionally unimplemented until OPENROUTER_API_KEY is provided.
        raise NotImplementedError(
            "OpenRouter client is not wired yet. Unset OPENROUTER_API_KEY "
            "to use the stub client, or implement the HTTP call here."
        )


def get_llm_client() -> LlmClient:
    key = (settings.OPENROUTER_API_KEY or "").strip()
    if key:
        return OpenRouterLlmClient(api_key=key, model=settings.OPENROUTER_MODEL)
    return StubLlmClient()
