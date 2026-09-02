# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa
from app.api.v1.endpoints import categorias, tareas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tareas.router)
app.include_router(categorias.router)


@app.get("/")
def root():
    return {"mensaje": "Acadex funcionando"}
