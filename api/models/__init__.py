from sqlmodel import SQLModel


# Create common Base to be used by all models
class Base(SQLModel):
    pass


from api.models.authentication import *  # noqa: E402, F403
from api.models.user import *  # noqa: E402, F403
from api.models.permission import *  # noqa: E402, F403
from api.models.ingredient import *  # noqa: E402, F403
from api.models.recipe import *  # noqa: E402, F403
