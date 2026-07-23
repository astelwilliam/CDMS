from app.db.session import Base  # noqa: F401
# Import all models so Alembic can detect them
from app.models import *  # noqa: F401,F403
