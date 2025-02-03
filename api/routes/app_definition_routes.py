from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import update
from sqlmodel import select

from api.core.authentication import get_admin_user, verify_access_token
from api.core.database import SessionDep
from api.models.app_definition import (
    AppDefinition,
    AppDefinitionCreateSchema,
    AppDefinitionDashboardSchema,
    AppDefinitionDetailSchema,
    AppDefinitionUpdateSchema,
)

router = APIRouter(
    prefix="/app-definition",
    dependencies=[Depends(verify_access_token)],
    tags=["AppDefinition"],
)


@router.get(
    "/",
    response_model=list[AppDefinitionDashboardSchema],
)
def get_all_apps(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    apps = session.exec(
        select(AppDefinition)
        .order_by(AppDefinition.due_date.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return apps


@router.get("/active/", response_model=list[AppDefinitionDashboardSchema])
def get_active_apps(session: SessionDep):
    apps = session.exec(
        select(AppDefinition).where(
            AppDefinition.start_date < datetime.now(),
            AppDefinition.due_date > datetime.now(),
        )
    ).all()
    return apps


@router.get(
    "/{app_id}/",
    response_model=AppDefinitionDetailSchema,
)
def get_app_definition_by_id(
    app_id: int,
    session: SessionDep,
):
    app_def = session.exec(
        select(AppDefinition).where(AppDefinition.id == app_id)
    ).first()
    if not app_def:
        raise HTTPException(
            status_code=404, detail=f"App Definition with id {app_id} not found."
        )
    return app_def


@router.post(
    "/",
    response_model=AppDefinitionDetailSchema,
    dependencies=[Depends(get_admin_user)],
)
def create_app_definition(app_def: AppDefinitionCreateSchema, session: SessionDep):
    db_app_dev = AppDefinition.model_validate(app_def)
    session.add(db_app_dev)
    session.commit()
    session.refresh(db_app_dev)
    return db_app_dev


@router.put(
    "/{app_def_id}/",
    response_model=AppDefinitionDetailSchema,
    dependencies=[Depends(get_admin_user)],
)
def update_app_definition(
    app_def_id: int, app_def: AppDefinitionUpdateSchema, session: SessionDep
):
    existing_app_def = session.exec(
        select(AppDefinition).where(AppDefinition.id == app_def_id)
    ).first()
    if existing_app_def:
        update_stmt = (
            update(AppDefinition)
            .where(AppDefinition.id == app_def_id)
            .values(**app_def.model_dump(exclude_unset=True))
            .execution_options(synchronize_session="fetch")
        )
        session.exec(update_stmt)
        session.commit()
        session.refresh(existing_app_def)
        return existing_app_def
    else:
        raise HTTPException(
            status_code=404, detail=f"App Definition with id {app_def_id} not found."
        )


@router.delete("/{app_def_id}/", dependencies=[Depends(get_admin_user)])
def delete_app_definition(app_def_id: int, session: SessionDep):
    existing_app_def = session.exec(
        select(AppDefinition).where(AppDefinition.id == app_def_id)
    ).first()
    if existing_app_def:
        session.delete(existing_app_def)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"App Definition with id {app_def_id} not found."
        )
