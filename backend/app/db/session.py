from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=settings.database_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
