from sqlmodel import create_engine, Session, SQLModel

from . import config

settings = config.get_settings()

DATABASE_URL = f"{settings.database}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
