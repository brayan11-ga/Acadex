# backend/app/api/v1/endpoints/tareas.py
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from app.schemas.archivo import ArchivoResponse
from app.services import archivo_service
from app.schemas.tarea import IntegranteAsignadoResponse

from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaResponse, TareaPropuestaIA
from app.services import tarea_service
from app.services import ia_service
from app.schemas.tarea import TareaGrupalCreate

router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return tarea_service.crear_tarea(db, datos, usuario_actual)


@router.post("/con-pdf", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea_con_pdf(
    datos: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    """Crea una tarea personal y registra su PDF en la misma transacción."""
    try:
        datos_tarea = TareaCreate.model_validate_json(datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Los datos de la tarea no son válidos.",
        ) from error

    if not archivo.filename or not archivo.filename.lower().endswith(".pdf") or archivo.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El archivo adjunto de esta operación debe ser un PDF.",
        )
    return tarea_service.crear_tarea_con_pdf(db, datos_tarea, usuario_actual, archivo)

@router.post("/grupos/{id_grupo}", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea_grupal(
    id_grupo: int,
    datos: TareaGrupalCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.crear_tarea_grupal(db, id_grupo, datos, usuario_actual)


@router.get("/", response_model=List[TareaResponse])
def listar_tareas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas(db, usuario_actual.id_usuario)


@router.get("/calendario", response_model=List[TareaResponse])
def listar_tareas_calendario(
    desde: date,
    hasta: date,
    id_usuario: Optional[int] = None,
    id_grupo: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas_calendario(
        db, desde, hasta, usuario_actual.id_usuario, id_usuario, id_grupo
    )


@router.get("/asignadas/mias", response_model=List[TareaResponse])
def listar_tareas_asignadas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas_asignadas(db, usuario_actual.id_usuario)


@router.get("/{id_tarea}", response_model=TareaResponse)
def obtener_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.obtener_tarea(db, id_tarea, usuario_actual.id_usuario)


@router.put("/{id_tarea}", response_model=TareaResponse)
def actualizar_tarea(
    id_tarea: int,
    datos: TareaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.actualizar_tarea(db, id_tarea, datos, usuario_actual.id_usuario)


@router.delete("/{id_tarea}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    tarea_service.eliminar_tarea(db, id_tarea, usuario_actual.id_usuario)
    

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

    return ia_service.analizar_documento_con_ia(
        db, archivo, usuario_actual.id_usuario
    )

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
def listar_archivos(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return archivo_service.listar_archivos_de_tarea(db, id_tarea, usuario_actual.id_usuario)


@router.get("/{id_tarea}/archivos/{id_archivo}")
def descargar_archivo(
    id_tarea: int,
    id_archivo: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    archivo, ruta = archivo_service.obtener_archivo_para_descarga(
        db, id_tarea, id_archivo, usuario_actual.id_usuario
    )
    encabezados = {
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "private, no-store",
    }
    tipo_mime = archivo_service.TIPOS_MIME[archivo.tipo]
    if isinstance(ruta, bytes):
        from urllib.parse import quote

        encabezados["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(archivo.nombre, safe='')}"
        return Response(content=ruta, media_type=tipo_mime, headers=encabezados)
    return FileResponse(
        path=ruta,
        media_type=tipo_mime,
        filename=archivo.nombre,
        headers=encabezados,
    )


@router.delete(
    "/{id_tarea}/archivos/{id_archivo}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_archivo(
    id_tarea: int,
    id_archivo: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    archivo_service.eliminar_archivo_tarea(db, id_tarea, id_archivo, usuario_actual.id_usuario)

@router.get("/grupos/{id_grupo}", response_model=List[TareaResponse])
def listar_tareas_de_grupo(
    id_grupo: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_tareas_de_grupo(db, id_grupo, usuario_actual.id_usuario)

@router.get("/{id_tarea}/asignados", response_model=List[IntegranteAsignadoResponse])
def listar_asignados(
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return tarea_service.listar_asignados_de_tarea(db, id_tarea, usuario_actual.id_usuario)
