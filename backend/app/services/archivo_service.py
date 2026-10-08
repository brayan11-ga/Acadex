# backend/app/services/archivo_service.py
import os
import shutil
from datetime import datetime
from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.archivo import Archivo
from app.repositories import (
    archivo_repository,
    tarea_repository,
    asignacion_tarea_repository,
    grupo_repository,
    notificacion_repository,
)

DIRECTORIO_BASE_UPLOADS = "uploads/tareas"
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5MB

TIPOS_PERMITIDOS = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "JPG",
    "image/png": "PNG",
}


def subir_archivo_tarea(db: Session, id_tarea: int, archivo: UploadFile, id_usuario: int) -> Archivo:
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if not tarea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    if not asignacion_tarea_repository.usuario_tiene_asignacion(db, id_tarea, id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes esta tarea asignada",
        )

    tipo = TIPOS_PERMITIDOS.get(archivo.content_type)
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no admitido. Usa PDF, DOCX, JPG o PNG.",
        )

    archivo.file.seek(0, 2)
    tamano = archivo.file.tell()
    archivo.file.seek(0)
    if tamano > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 5MB.",
        )

    carpeta_tarea = os.path.join(DIRECTORIO_BASE_UPLOADS, str(id_tarea))
    os.makedirs(carpeta_tarea, exist_ok=True)

    nombre_guardado = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}"
    ruta_relativa = os.path.join(carpeta_tarea, nombre_guardado)

    with open(ruta_relativa, "wb") as destino:
        shutil.copyfileobj(archivo.file, destino)

    nuevo_archivo = archivo_repository.crear_archivo(
        db, nombre=archivo.filename, tamano=tamano, tipo=tipo, ruta=ruta_relativa, id_tarea=id_tarea
    )

    if tarea.id_grupo is not None:
        lider = grupo_repository.obtener_lider_de_grupo(db, tarea.id_grupo)
        if lider:
            notificacion_repository.crear_notificacion(
                db,
                titulo="Nuevo avance subido",
                detalles=f"Se subió un archivo en la tarea '{tarea.nombre}'",
                tipo="archivo_tarea",
                id_usuario=lider.id_usuario,
                id_tarea=id_tarea,
            )

    return nuevo_archivo


def listar_archivos_de_tarea(db: Session, id_tarea: int) -> List[Archivo]:
    return archivo_repository.obtener_archivos_de_tarea(db, id_tarea)