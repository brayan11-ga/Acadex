# backend/app/api/v1/endpoints/tareas.py
from datetime import date
from typing import List, Optional
from fastapi import File, UploadFile
from app.schemas.archivo import ArchivoResponse
from app.services import archivo_service
from app.schemas.tarea import IntegranteAsignadoResponse

from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaResponse, TareaPropuestaIA
from app.services import tarea_service
from app.services import ia_service
from app.schemas.tarea import TareaGrupalCreate
from app.dependencies.auth import get_usuario_actual, requerir_lider_de_grupo

router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    # Si la tarea no viene asociada a un grupo, es una tarea personal:
    # asignamos el id_usuario real del token (nunca el que mande el frontend)
    if datos.id_grupo is None:
        datos.id_usuario = usuario_actual.id_usuario
    return tarea_service.crear_tarea(db, datos)

@router.post("/grupos/{id_grupo}", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea_grupal(
    id_grupo: int,
    datos: TareaGrupalCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requerir_lider_de_grupo),
):
    return tarea_service.crear_tarea_grupal(db, id_grupo, datos)


@router.get("/", response_model=List[TareaResponse])
def listar_tareas(db: Session = Depends(get_db)):
    return tarea_service.listar_tareas(db)


@router.get("/calendario", response_model=List[TareaResponse])
def listar_tareas_calendario(
    desde: date,
    hasta: date,
    id_usuario: Optional[int] = None,
    id_grupo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return tarea_service.listar_tareas_calendario(db, desde, hasta, id_usuario, id_grupo)


@router.get("/asignadas/mias", response_model=List[TareaResponse])
def listar_tareas_asignadas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas_asignadas(db, usuario_actual.id_usuario)


@router.get("/{id_tarea}", response_model=TareaResponse)
def obtener_tarea(id_tarea: int, db: Session = Depends(get_db)):
    return tarea_service.obtener_tarea(db, id_tarea)


@router.put("/{id_tarea}", response_model=TareaResponse)
def actualizar_tarea(id_tarea: int, datos: TareaUpdate, db: Session = Depends(get_db)):
    return tarea_service.actualizar_tarea(db, id_tarea, datos)


@router.delete("/{id_tarea}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(id_tarea: int, db: Session = Depends(get_db)):
    tarea_service.eliminar_tarea(db, id_tarea)
    

@router.post("/analizar-documento", response_model=TareaPropuestaIA)
def analizar_documento(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """
    Recibe un archivo PDF, lo analiza en memoria usando Gemini IA y
    devuelve una propuesta de tarea sin guardarla en la base de datos.
    """
    if archivo.content_type != "application/pdf" or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se admiten documentos en formato PDF."
        )
        
    # Verificar magic bytes del PDF
    header = archivo.file.read(5)
    if header != b"%PDF-":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El archivo no es un PDF válido."
        )
    archivo.file.seek(0)
    
    # Validar tamaño aproximado (ej. 5MB) leyendo el buffer
    archivo.file.seek(0, 2) # Ir al final del archivo
    tamanio = archivo.file.tell()
    archivo.file.seek(0) # Volver al inicio para que pdfplumber pueda leerlo
    
    if tamanio > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 5MB."
        )

    return ia_service.analizar_documento_con_ia(db, archivo)

# ... @router.post("/") def crear_tarea(...) ...

#estas son rutas para los archivos del modulo de grupos vale
@router.post("/{id_tarea}/archivos", response_model=ArchivoResponse, status_code=status.HTTP_201_CREATED)
def subir_archivo(
    id_tarea: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return archivo_service.subir_archivo_tarea(db, id_tarea, archivo, usuario_actual.id_usuario)


@router.get("/{id_tarea}/archivos", response_model=List[ArchivoResponse])
def listar_archivos(id_tarea: int, db: Session = Depends(get_db)):
    return archivo_service.listar_archivos_de_tarea(db, id_tarea)

@router.get("/grupos/{id_grupo}", response_model=List[TareaResponse])
def listar_tareas_de_grupo(
    id_grupo: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas_de_grupo(db, id_grupo)

@router.get("/{id_tarea}/asignados", response_model=List[IntegranteAsignadoResponse])
def listar_asignados(id_tarea: int, db: Session = Depends(get_db)):
    return tarea_service.listar_asignados_de_tarea(db, id_tarea)