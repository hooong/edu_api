from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from edu_register_api.enums import AppEnv
from edu_register_api.models import Base
from edu_register_api.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, echo=(settings.APP_ENV in [AppEnv.LOCAL, AppEnv.DEV])
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
