from core.settings import settings
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

db = SQLAlchemy(metadata=MetaData(schema=settings.postgres_schema))
migration = Migrate()
