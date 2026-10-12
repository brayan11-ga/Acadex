# DATABASE
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASES_URL")

if not DATABASE_URL:
    raise RuntimeError("Falta la variable de entorno DATABASES_URL en el .env")

engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base()