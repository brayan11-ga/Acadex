from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


api = FastAPI(title="Acadex API", lifespan=lifespan)

api.include_router(router)

api = FastAPI(title="Acadex API")

api.include_router(router)


@api.get("/")
def root():
    return {"mensaje": "Acadex funcionando"}


# Wrap the whole application so CORS headers are also added to unhandled
# error responses produced by FastAPI/Starlette's outer error middleware.
app = CORSMiddleware(
    app=api,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
