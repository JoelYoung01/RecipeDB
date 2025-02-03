from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.models.app_submission import (
    AppSubmission,
    AppSubmissionCreateSchema,
    AppSubmissionDetailSchema,
)

router = APIRouter(
    prefix="/app-submission",
    dependencies=[Depends(verify_access_token)],
    tags=["AppSubmission"],
)


@router.get(
    "/",
    tags=["AppSubmission"],
    response_model=list[AppSubmissionDetailSchema],
)
def get_all_users_app_submissions(session: SessionDep, current_user: CurrentUserDep):
    submissions = session.exec(
        select(AppSubmission).where(
            AppSubmission.created_by == current_user.id,
        )
    )
    return submissions


@router.get(
    "/{app_id}/",
    tags=["AppSubmission"],
    response_model=list[AppSubmissionDetailSchema],
)
def get_app_submission_by_app_id(
    app_id: int, session: SessionDep, current_user: CurrentUserDep
):
    submissions = session.exec(
        select(AppSubmission).where(
            AppSubmission.app_definition_id == app_id,
            AppSubmission.created_by == current_user.id,
        )
    )
    if not submissions:
        raise HTTPException(
            status_code=404,
            detail=f"App Submissions for app with id {app_id} not found.",
        )
    return submissions


@router.post(
    "/",
    tags=["AppSubmission"],
    response_model=AppSubmissionDetailSchema,
)
def create_app_submission(
    submission: AppSubmissionCreateSchema,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    new_submission = submission.model_dump()
    new_submission["created_on"] = datetime.now(timezone.utc).isoformat()
    new_submission["created_by"] = current_user.id

    db_submission = AppSubmission.model_validate(new_submission)

    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    return db_submission


@router.delete("/{submission_id}/", tags=["AppSubmission"])
def delete_app_submission(submission_id: int, session: SessionDep):
    existing_submission = session.exec(
        select(AppSubmission).where(AppSubmission.id == submission_id)
    ).first()
    if existing_submission:
        session.delete(existing_submission)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"App Submission with id {submission_id} not found."
        )
