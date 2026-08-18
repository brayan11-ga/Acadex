import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# importa la conexion bd
load_dotenv()


DATABASE_URL=os.getenv("DATABASES_URL")


engine= create_engine("DATABASES_URL")


engine =create_engine(DATABASE_URL)
sessionLocal =sessionmaker(autocommit=False, autoflush=False,bind=engine)


base=declarative_base()
