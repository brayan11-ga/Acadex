from fastapi import FastAPI

app = FastAPI(
    title="Acadex API",
    description="API para la gestión inteligente de tareas y actividades académicas.",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Acadex API funcionando"
    }