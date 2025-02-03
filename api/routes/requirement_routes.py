from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlmodel import select

from api.core.authentication import verify_access_token
from api.core.database import SessionDep
from api.models.requirement import (
    Requirement,
    RequirementCreateSchema,
    RequirementDetailSchema,
    RequirementUpdateSchema,
)

router = APIRouter(
    prefix="/requirement",
    dependencies=[Depends(verify_access_token)],
    tags=["Requirement"],
)


@router.post(
    "/",
    tags=["Requirement"],
    response_model=RequirementDetailSchema,
)
def create_requirement(
    requirement: RequirementCreateSchema,
    session: SessionDep,
):
    db_req = Requirement.model_validate(requirement)
    session.add(db_req)
    session.commit()
    session.refresh(db_req)
    return db_req


@router.put(
    "/{req_id}/",
    tags=["Requirement"],
    response_model=RequirementDetailSchema,
)
def update_requirement(
    req_id: int,
    requirement: RequirementUpdateSchema,
    session: SessionDep,
):
    existing_requirement = session.exec(
        select(Requirement).where(Requirement.id == req_id)
    ).first()
    if existing_requirement:
        update_stmt = (
            update(Requirement)
            .where(Requirement.id == req_id)
            .values(**requirement.model_dump(exclude_unset=True))
            .execution_options(synchronize_session="fetch")
        )
        session.exec(update_stmt)
        session.commit()
        session.refresh(existing_requirement)
        return existing_requirement
    else:
        raise HTTPException(
            status_code=404, detail=f"Requirement with id {req_id} not found."
        )


@router.delete("/{req_id}/", tags=["Requirement"])
def delete_requirement(req_id: int, session: SessionDep):
    existing_requirement = session.exec(
        select(Requirement).where(Requirement.id == req_id)
    ).first()
    if existing_requirement:
        session.delete(existing_requirement)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Requirement with id {req_id} not found."
        )
