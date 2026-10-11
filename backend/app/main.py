# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router
import app.models  # noqa

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
