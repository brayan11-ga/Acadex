# app/main.py
# app/main.py
from fastapi import FastAPI

import app.models  # noqa - registra todos los modelos antes de usar la BD
from app.api.v1.endpoints import tareas

app = FastAPI()

app.include_router(tareas.router)


@app.get("/")
def root():
    return {"mensaje": "Acadex funcionando"}
