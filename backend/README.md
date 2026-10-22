# Backend de Acadex

El backend es una API FastAPI con SQLAlchemy, Pydantic y PostgreSQL. La ruta de entrada es **app.main:app**; una instancia en ejecución publica la documentación OpenAPI en **/docs**.

Para ejecutar el sistema completo por primera vez se recomienda el [README raíz](../README.md) con Docker Compose. Esta guía es para desarrollo manual del backend.

## Preparación local

La configuración de contenedores y CI usa Python 3.14. Crea un entorno virtual desde backend e instala las dependencias fijadas:

~~~sh
python -m venv .venv
# Activa .venv según tu sistema operativo.
python -m pip install -r requirements.txt
~~~

Copia backend/.env.example a backend/.env solo si aún no tienes configuración local y completa una conexión a PostgreSQL que controles. No copies credenciales de Supabase, Gemini, SMTP ni producción al repositorio.

En PowerShell:

~~~powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
~~~

La plantilla explica las variables opcionales para correo, Gemini y almacenamiento. CORS_ORIGINS debe coincidir con el origen del frontend local. Para el esquema, el historial y las precauciones de una base existente, consulta [database/README.md](../database/README.md).

## Ejecutar

Con PostgreSQL local preparado y el esquema aplicado de forma segura:

~~~sh
python -m uvicorn app.main:app --reload
~~~

La API escucha el puerto 8000 salvo que se cambie el comando. Consulta <http://localhost:8000/docs> en ejecución. No uses este procedimiento como receta de producción: los secretos, el arranque de migraciones y la configuración de proveedores deben gestionarse por el entorno de despliegue correspondiente.

## Pruebas

Desde backend:

~~~sh
python -m pytest test tests -q
~~~

Las pruebas que requieren PostgreSQL tienen guardas específicas y se ejecutan con el Compose aislado desde la raíz del repositorio. Sigue [docs/calidad-y-pruebas.md](../docs/calidad-y-pruebas.md) y no apuntes las pruebas a una base existente.

## Organización

- app/api: routers y endpoints de la API.
- app/config: configuración y validaciones de entorno.
- app/models, schemas, repositories y services: datos, contratos y lógica de aplicación.
- app/db: conexión y soporte de persistencia.
- alembic/versions: fuente vigente de las migraciones.
- test y tests: suites de prueba.

La descripción de cómo se comunican estas capas está en [docs/arquitectura.md](../docs/arquitectura.md).
