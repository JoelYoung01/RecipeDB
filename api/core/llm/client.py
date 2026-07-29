"""OpenRouter LLM client with a deterministic stub fallback."""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from api.core.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


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


def _repair_json_text(text: str) -> str:
    """Apply cheap fixes for common LLM JSON quirks before json.loads."""
    repaired = text.strip()
    # Normalize fancy whitespace / quotes that break strict JSON.
    repaired = (
        repaired.replace("\u00a0", " ")
        .replace("\u202f", " ")
        .replace("\u2009", " ")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )
    # Trailing commas before } or ]
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    return repaired


def _extract_json_payload(text: str) -> Any:
    """Parse JSON from a model reply, tolerating markdown fences / prose."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Empty LLM response")

    candidates: list[str] = [cleaned]
    for match in re.finditer(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE):
        candidates.append(match.group(1).strip())

    # Largest object / array substrings as a last resort.
    for opener, closer in (("{", "}"), ("[", "]")):
        start = cleaned.find(opener)
        end = cleaned.rfind(closer)
        if start != -1 and end > start:
            candidates.append(cleaned[start : end + 1])

    # Also try repaired variants of each candidate.
    expanded: list[str] = []
    for candidate in candidates:
        expanded.append(candidate)
        repaired = _repair_json_text(candidate)
        if repaired != candidate:
            expanded.append(repaired)

    errors: list[str] = []
    for candidate in expanded:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            errors.append(str(exc))
    raise ValueError(
        "Could not parse JSON from LLM response: "
        + (errors[-1] if errors else "unknown")
    )


def _normalize_parsed(parsed: Any, *, mode: str) -> dict[str, Any]:
    """Coerce common model shapes into {ideas: [...]} or {recipes: [...]}."""
    if isinstance(parsed, dict):
        if mode == "ideate":
            if isinstance(parsed.get("ideas"), list):
                return parsed
            for key in ("options", "meals", "suggestions", "dinner_ideas"):
                if isinstance(parsed.get(key), list):
                    return {"ideas": parsed[key]}
        else:
            if isinstance(parsed.get("recipes"), list):
                return parsed
            for key in ("dinners", "meals", "dishes"):
                if isinstance(parsed.get(key), list):
                    return {"recipes": parsed[key]}
        # Single idea / recipe object
        if mode == "ideate" and ("title" in parsed or "justification" in parsed):
            return {"ideas": [parsed]}
        if mode == "build" and (
            "ingredients" in parsed or "instructions" in parsed or "title" in parsed
        ):
            return {"recipes": [parsed]}
        return parsed

    if isinstance(parsed, list):
        return {"ideas": parsed} if mode == "ideate" else {"recipes": parsed}

    raise ValueError(f"Unexpected LLM JSON type: {type(parsed).__name__}")


def _infer_mode(messages: list[ChatMessage]) -> str:
    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    return "build" if "BUILD_RECIPES" in last_user else "ideate"


class OpenRouterLlmClient(LlmClient):
    """Chat Completions client against OpenRouter's OpenAI-compatible API."""

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
        mode = _infer_mode(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        else:
            # Ask OpenRouter for a JSON object when we are not in a tool loop.
            # Mercury/OpenAI-compatible models honor this more reliably than
            # prompt-only "JSON only" instructions.
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.FRONTEND_HOST,
            "X-Title": settings.PROJECT_NAME,
        }

        last_error: Exception | None = None
        # One retry helps when a model occasionally emits truncated / invalid JSON.
        for attempt in range(2):
            try:
                return await self._complete_once(
                    payload, headers=headers, mode=mode, attempt=attempt
                )
            except RuntimeError as exc:
                last_error = exc
                if attempt == 0 and "non-JSON content" in str(exc):
                    logger.warning(
                        "OpenRouter %s JSON parse failed on attempt 1; retrying once",
                        mode,
                    )
                    continue
                raise
        raise RuntimeError(str(last_error) if last_error else "OpenRouter failed")

    async def _complete_once(
        self,
        payload: dict[str, Any],
        *,
        headers: dict[str, str],
        mode: str,
        attempt: int,
    ) -> LlmTurnResult:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    OPENROUTER_CHAT_URL, headers=headers, json=payload
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text[:500]
            raise RuntimeError(f"OpenRouter error {response.status_code}: {detail}")

        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenRouter returned non-JSON response") from exc

        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("OpenRouter response missing choices")

        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        if isinstance(content, list):
            # Some providers return content parts; join text segments.
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )

        raw_tool_calls = message.get("tool_calls") or []
        tool_calls: list[dict[str, Any]] = [
            tc for tc in raw_tool_calls if isinstance(tc, dict)
        ]

        text = content if isinstance(content, str) else str(content)
        parsed: Any = None
        if text.strip():
            try:
                parsed = _normalize_parsed(_extract_json_payload(text), mode=mode)
            except ValueError as exc:
                # Tool-only turns may omit JSON content; otherwise fail loudly so
                # the wizard does not silently pad with filler ideas/recipes.
                if tool_calls:
                    logger.warning(
                        "OpenRouter reply was not valid structured JSON "
                        "(mode=%s attempt=%s); returning tool_calls only",
                        mode,
                        attempt + 1,
                    )
                else:
                    raise RuntimeError(
                        f"OpenRouter returned non-JSON content for {mode}: {exc}"
                    ) from exc

        return LlmTurnResult(
            content=text,
            parsed=parsed,
            tool_calls=tool_calls,
            stubbed=False,
        )


def get_llm_client() -> LlmClient:
    key = (settings.OPENROUTER_API_KEY or "").strip()
    if key:
        return OpenRouterLlmClient(api_key=key, model=settings.OPENROUTER_MODEL)
    return StubLlmClient()
