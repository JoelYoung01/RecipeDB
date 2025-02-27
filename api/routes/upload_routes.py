from datetime import UTC, datetime
import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from pathlib import Path

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.config import settings
from api.core.logging import logger
from api.core.database import SessionDep
from api.models import Upload
from api.schemas import UploadFileResponse

router = APIRouter(
    prefix="/upload", dependencies=[Depends(verify_access_token)], tags=["Upload"]
)

UPLOAD_PATH = Path(settings.UPLOAD_DIR)
UPLOAD_PATH.mkdir(exist_ok=True)


@router.post("/", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    # Create user-specific directory
    user_dir = UPLOAD_PATH / str(current_user.id)
    user_dir.mkdir(exist_ok=True)

    # Build file path with hash to avoid collision
    file_hash = secrets.token_hex(8)  # Generate a random hash
    original_file_name = ".".join(file.filename.split(".")[:-1])
    file_name = f"{original_file_name}_{file_hash}.{file.filename.split('.')[-1]}"

    # Set path and url
    file_path = user_dir / file_name
    file_url = f"/uploads/{current_user.id}/{file_name}"

    # Write file contents to disk
    file_saved = False
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        file_saved = True
    except Exception as e:
        logger.error(f"An error occurred while saving: {str(e)}")
    finally:
        await file.close()

    if not file_saved:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the file.",
        )

    # Build corresponding db entry for file
    db_file = Upload(
        created_by_id=current_user.id,
        created_on=datetime.now(UTC),
        url=file_url,
        file_path=str(file_path),
        name=file.filename,
    )

    session.add(db_file)
    session.commit()
    session.refresh(db_file)

    return db_file


@router.post("/avatar/")
async def upload_avatar(
    file: UploadFile,
    current_user: CurrentUserDep,
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Upload must be an image.")

    # Create avatars directory
    avatar_dir = UPLOAD_PATH / "avatars"
    avatar_dir.mkdir(exist_ok=True)

    # Save with user ID as filename
    file_ext = os.path.splitext(file.filename)[1]
    file_path = avatar_dir / f"{current_user.id}{file_ext}"

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    finally:
        await file.close()

    return {"filename": file_path.name, "path": str(file_path)}


@router.delete("/")
async def delete_upload(file_path: str, current_user: CurrentUserDep):
    # Construct the full path to the file
    full_path = UPLOAD_PATH / file_path

    # Check if the file exists and belongs to the current user
    if (
        not full_path.exists()
        or str(full_path).startswith(str(UPLOAD_PATH / str(current_user.id))) is False
        and current_user.admin is False
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied.",
        )

    # Delete the file
    os.remove(full_path)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
