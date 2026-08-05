from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.core.grocery import aggregate_grocery_items, normalize_item_key, window_bounds
from api.core.household import ensure_user_household, require_membership
from api.models import GroceryItemState, GroceryItemStatus, PlannedRecipe, Recipe
from api.schemas import (
    GroceryItem,
    GroceryItemStateUpdate,
    GroceryListResponse,
    GrocerySummaryResponse,
)

router = APIRouter(
    prefix="/grocery",
    dependencies=[Depends(verify_access_token)],
    tags=["Grocery"],
)


def _build_grocery_items(
    current_user: CurrentUserDep,
    session: SessionDep,
    *,
    include_deleted: bool = False,
) -> tuple[datetime, datetime, list[GroceryItem]]:
    start, end = window_bounds(datetime.now(UTC))
    household, _ = require_membership(session, current_user)

    planned = session.exec(
        select(PlannedRecipe)
        .where(
            PlannedRecipe.household_id == household.id,
            PlannedRecipe.planned_for >= start,
            PlannedRecipe.planned_for <= end,
        )
        .options(selectinload(PlannedRecipe.recipe).selectinload(Recipe.ingredients))
    ).all()

    aggregated = aggregate_grocery_items(list(planned))

    states = session.exec(
        select(GroceryItemState).where(
            GroceryItemState.household_id == household.id
        )
    ).all()
    state_by_key = {s.item_key: s for s in states}

    items: list[GroceryItem] = []
    for raw in aggregated:
        state = state_by_key.get(raw["key"])
        dismissed = bool(state and state.status == GroceryItemStatus.dismissed.value)
        deleted = bool(state and state.status == GroceryItemStatus.deleted.value)
        if deleted and not include_deleted:
            continue
        items.append(
            GroceryItem(
                **raw,
                dismissed=dismissed,
                deleted=deleted,
            )
        )

    return start, end, items


@router.get("/", response_model=GroceryListResponse)
def get_grocery_list(
    current_user: CurrentUserDep,
    session: SessionDep,
    include_deleted: bool = False,
):
    start, end, items = _build_grocery_items(
        current_user, session, include_deleted=include_deleted
    )
    return GroceryListResponse(
        window_start=start,
        window_end=end,
        items=items,
    )


@router.get("/summary/", response_model=GrocerySummaryResponse)
def get_grocery_summary(
    current_user: CurrentUserDep,
    session: SessionDep,
):
    """Lightweight badge payload for Home — skips shipping the full item list."""
    start, end, items = _build_grocery_items(current_user, session)
    active_count = sum(1 for i in items if not i.dismissed and not i.deleted)
    return GrocerySummaryResponse(
        window_start=start,
        window_end=end,
        active_count=active_count,
    )


@router.put("/state/", response_model=GroceryItem)
def update_grocery_item_state(
    body: GroceryItemStateUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    key = normalize_item_key(body.item_key)
    if not key:
        raise HTTPException(
            status_code=400, detail="Missing grocery item. Refresh and try again."
        )

    if body.status is not None and body.status not in {
        GroceryItemStatus.dismissed.value,
        GroceryItemStatus.deleted.value,
    }:
        raise HTTPException(
            status_code=400,
            detail="That grocery status isn’t valid. Refresh and try again.",
        )

    household = ensure_user_household(session, current_user)

    existing = session.exec(
        select(GroceryItemState).where(
            GroceryItemState.household_id == household.id,
            GroceryItemState.item_key == key,
        )
    ).first()

    if body.status is None:
        if existing:
            session.delete(existing)
            session.commit()
    else:
        status_value = GroceryItemStatus(body.status).value
        if existing:
            existing.status = status_value
            existing.updated_on = datetime.now(UTC)
            session.add(existing)
        else:
            session.add(
                GroceryItemState(
                    created_by_id=current_user.id,
                    household_id=household.id,
                    item_key=key,
                    status=status_value,
                    updated_on=datetime.now(UTC),
                )
            )
        session.commit()

    # Return the item as it appears in the current window (if present)
    grocery = get_grocery_list(
        current_user=current_user, session=session, include_deleted=True
    )
    for item in grocery.items:
        if item.key == key:
            return item

    # Item may not be in the window (e.g. no longer planned); return a stub
    return GroceryItem(
        key=key,
        name=body.item_key.strip() or key,
        category="Other",
        quantities=[],
        quantity_display="",
        recipes=[],
        recipe_titles="",
        source_ingredient_ids=[],
        dismissed=body.status == GroceryItemStatus.dismissed.value,
        deleted=body.status == GroceryItemStatus.deleted.value,
    )
