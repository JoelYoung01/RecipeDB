from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session

from api.core.config import settings
from api.core.seed_database import seed_database

connect_args = {"check_same_thread": False}
engine = create_engine(settings.SQLITE_DATABASE_URL, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def init_db(session: Session) -> None:
    seed_database(session)
