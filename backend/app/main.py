from fastapi import FastAPI
import app.models  # noqa - registra todos los modelos antes de usar la BD
from app.api.v1.router import router

app = FastAPI()

app.include_router(router)

@app.get("/")
def root():
    return {"mensaje": "Acadex funciona correctamente"}
