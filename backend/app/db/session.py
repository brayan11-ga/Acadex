from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(
    settings.database_url,
    connect_args={"options": "-c lc_messages=C"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)