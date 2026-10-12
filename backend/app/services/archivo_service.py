import logging
import os
import unicodedata
import uuid
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Iterator, List

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.archivo import Archivo
from app.repositories import (
    archivo_repository,
    asignacion_tarea_repository,
    grupo_repository,
    notificacion_repository,
    tarea_repository,
)

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DIRECTORIO_BASE_UPLOADS = Path(
    os.getenv("ACADEX_UPLOADS_DIR", str(BACKEND_ROOT / "uploads" / "tareas"))
).expanduser().resolve()
DIRECTORIO_UPLOADS_HISTORICOS = (BACKEND_ROOT / "uploads" / "tareas").resolve()
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024

TIPOS_PERMITIDOS = {
    ".pdf": ("application/pdf", "PDF"),
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "DOCX",
    ),
    ".jpg": ("image/jpeg", "JPG"),
    ".jpeg": ("image/jpeg", "JPG"),
    ".png": ("image/png", "PNG"),
}

TIPOS_MIME = {
    "PDF": "application/pdf",
    "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "JPG": "image/jpeg",
    "PNG": "image/png",
}


def _normalizar_nombre(nombre: str | None) -> str:
    nombre_seguro = (nombre or "").replace("\\", "/").rsplit("/", 1)[-1]
    nombre_seguro = unicodedata.normalize("NFC", nombre_seguro).strip()
    nombre_seguro = "".join(caracter for caracter in nombre_seguro if caracter.isprintable())
    if not nombre_seguro or nombre_seguro in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de archivo inválido.")

    if len(nombre_seguro) > 100:
        extension = Path(nombre_seguro).suffix
        base = nombre_seguro[:-len(extension)] if extension else nombre_seguro
        nombre_seguro = f"{base[: max(1, 100 - len(extension))]}{extension}"
    return nombre_seguro


def _validar_archivo(archivo: UploadFile) -> tuple[str, str, int]:
    nombre = _normalizar_nombre(archivo.filename)
    extension = Path(nombre).suffix.lower()
    tipo_configurado = TIPOS_PERMITIDOS.get(extension)
    content_type = (archivo.content_type or "").split(";", 1)[0].strip().lower()

    if not tipo_configurado or tipo_configurado[0] != content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no admitido. Usa PDF, DOCX, JPG o PNG.",
        )

    try:
        archivo.file.seek(0, os.SEEK_END)
        tamano = archivo.file.tell()
        archivo.file.seek(0)
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo leer el archivo.",
        ) from error

    if tamano == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo está vacío.")
    if tamano > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="El archivo supera el límite de 5MB.",
        )

    try:
        encabezado = archivo.file.read(8)
        archivo.file.seek(0)

        if extension == ".pdf" and not encabezado.startswith(b"%PDF-"):
            raise ValueError("PDF inválido")
        if extension in {".jpg", ".jpeg"} and not encabezado.startswith(b"\xff\xd8\xff"):
            raise ValueError("JPEG inválido")
        if extension == ".png" and not encabezado.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("PNG inválido")
        if extension == ".docx":
            with zipfile.ZipFile(archivo.file) as documento:
                nombres = set(documento.namelist())
                if "[Content_Types].xml" not in nombres or "word/document.xml" not in nombres:
                    raise ValueError("DOCX inválido")
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as error:
        archivo.file.seek(0)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido del archivo no coincide con su formato.",
        ) from error
    finally:
        archivo.file.seek(0)

    return nombre, tipo_configurado[1], tamano


def _dentro_de(ruta: Path, raiz: Path) -> Path:
    ruta_resuelta = ruta.resolve()
    raiz_resuelta = raiz.resolve()
    try:
        ruta_resuelta.relative_to(raiz_resuelta)
    except ValueError as error:
        raise ValueError("La ruta del archivo está fuera del almacenamiento permitido") from error
    return ruta_resuelta


def _resolver_ruta(ruta_guardada: str, id_tarea_esperada: int | None = None) -> Path:
    ruta_normalizada = ruta_guardada.replace("\\", "/")
    ruta_posix = PurePosixPath(ruta_normalizada)
    if ruta_posix.is_absolute() or ".." in ruta_posix.parts:
        raise ValueError("La ruta almacenada no es válida")

    if ruta_normalizada.startswith("uploads/tareas/"):
        partes_relativas = ruta_posix.parts[2:]
        if not partes_relativas:
            raise ValueError("La ruta almacenada no es válida")
        if id_tarea_esperada is not None and partes_relativas[0] != str(id_tarea_esperada):
            raise ValueError("La ruta no pertenece a la tarea solicitada")
        rutas_candidatas = (
            _dentro_de(DIRECTORIO_UPLOADS_HISTORICOS.joinpath(*partes_relativas), DIRECTORIO_UPLOADS_HISTORICOS),
            _dentro_de(DIRECTORIO_BASE_UPLOADS.joinpath(*partes_relativas), DIRECTORIO_BASE_UPLOADS),
        )
        return next((ruta for ruta in rutas_candidatas if ruta.is_file()), rutas_candidatas[0])

    if not ruta_posix.parts:
        raise ValueError("La ruta almacenada no es válida")
    if id_tarea_esperada is not None and ruta_posix.parts[0] != str(id_tarea_esperada):
        raise ValueError("La ruta no pertenece a la tarea solicitada")
    return _dentro_de(DIRECTORIO_BASE_UPLOADS.joinpath(*ruta_posix.parts), DIRECTORIO_BASE_UPLOADS)


def _autorizacion_tarea(db: Session, id_tarea: int, id_usuario: int):
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    if tarea.id_usuario is not None:
        autorizado = tarea.id_usuario == id_usuario
    else:
        # Conserva el permiso que ya utilizaba la subida grupal: asignación directa a la tarea.
        autorizado = asignacion_tarea_repository.usuario_tiene_asignacion(db, id_tarea, id_usuario)

    if not autorizado:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta tarea.")
    return tarea


def _respuesta_archivo(archivo: Archivo, tarea, id_usuario: int) -> dict:
    return {
        "id_archivo": archivo.id_archivo,
        "nombre": archivo.nombre,
        "tamano": archivo.tamano,
        "tipo": archivo.tipo,
        "fecha_adjuncion": archivo.fecha_adjuncion,
        "id_tarea": archivo.id_tarea,
        "puede_eliminar": tarea.id_usuario == id_usuario or archivo.id_usuario_subida == id_usuario,
    }


def _guardar_binario(archivo: UploadFile, id_tarea: int, extension: str, tamano_esperado: int) -> tuple[Path, str]:
    carpeta_tarea = DIRECTORIO_BASE_UPLOADS / str(id_tarea)
    carpeta_tarea.mkdir(parents=True, exist_ok=True)

    nombre_interno = f"{uuid.uuid4().hex}{extension}"
    ruta_final = _dentro_de(carpeta_tarea / nombre_interno, DIRECTORIO_BASE_UPLOADS)
    ruta_temporal = ruta_final.with_name(f".{uuid.uuid4().hex}.uploading")
    escritos = 0

    try:
        with ruta_temporal.open("xb") as destino:
            while True:
                try:
                    bloque = archivo.file.read(1024 * 1024)
                except OSError as error:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No se pudo leer el archivo.",
                    ) from error
                if not bloque:
                    break
                escritos += len(bloque)
                if escritos > TAMANO_MAXIMO_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="El archivo supera el límite de 5MB.",
                    )
                destino.write(bloque)
        if escritos != tamano_esperado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo leer el archivo completo.")
        os.replace(ruta_temporal, ruta_final)
    except Exception:
        try:
            ruta_temporal.unlink(missing_ok=True)
        except OSError:
            logger.exception("No se pudo limpiar el archivo temporal de una subida fallida")
        raise
    finally:
        archivo.file.seek(0)

    return ruta_final, f"{id_tarea}/{nombre_interno}"


def _quitar_binario_si_huerfano(ruta: Path) -> None:
    try:
        ruta.unlink(missing_ok=True)
    except OSError:
        logger.exception("No se pudo limpiar el binario después de fallar el registro del adjunto")


@contextmanager
def _archivos_en_cuarentena(rutas: List[Path]) -> Iterator[None]:
    movidos: list[tuple[Path, Path]] = []
    try:
        rutas_unicas = {ruta.resolve() for ruta in rutas}
        for ruta in rutas_unicas:
            if not ruta.exists():
                continue
            if not ruta.is_file():
                raise OSError("El almacenamiento contiene una ruta que no es un archivo")
            temporal = ruta.with_name(f".{ruta.name}.{uuid.uuid4().hex}.deleting")
            os.replace(ruta, temporal)
            movidos.append((ruta, temporal))
        yield
    except BaseException:
        for original, temporal in reversed(movidos):
            try:
                if temporal.exists():
                    os.replace(temporal, original)
            except OSError:
                logger.exception("No se pudo restaurar un adjunto tras fallar la operación de base de datos")
        raise
    else:
        for _, temporal in movidos:
            try:
                temporal.unlink(missing_ok=True)
            except OSError:
                # El registro ya no es visible; el archivo oculto puede limpiarse después sin afectar a la API.
                logger.exception("No se pudo retirar el binario en cuarentena")


def subir_archivo_tarea(db: Session, id_tarea: int, archivo: UploadFile, id_usuario: int) -> dict:
    tarea = _autorizacion_tarea(db, id_tarea, id_usuario)
    nombre, tipo, tamano = _validar_archivo(archivo)
    extension = Path(nombre).suffix.lower()
    try:
        ruta_fisica, ruta_relativa = _guardar_binario(archivo, id_tarea, extension, tamano)
    except HTTPException:
        raise
    except OSError as error:
        logger.exception("El almacenamiento no pudo completar la subida")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento no está disponible.",
        ) from error

    try:
        nuevo_archivo = archivo_repository.crear_archivo(
            db,
            nombre=nombre,
            tamano=tamano,
            tipo=tipo,
            ruta=ruta_relativa,
            id_tarea=id_tarea,
            id_usuario_subida=id_usuario,
        )
    except Exception as error:
        db.rollback()
        _quitar_binario_si_huerfano(ruta_fisica)
        logger.exception("No se pudo registrar el adjunto en la base de datos")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo guardar el adjunto.",
        ) from error

    respuesta = _respuesta_archivo(nuevo_archivo, tarea, id_usuario)

    if tarea.id_grupo is not None:
        try:
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
        except Exception:
            db.rollback()
            logger.exception("No se pudo crear la notificación del nuevo adjunto")

    return respuesta


def listar_archivos_de_tarea(db: Session, id_tarea: int, id_usuario: int) -> List[dict]:
    tarea = _autorizacion_tarea(db, id_tarea, id_usuario)
    return [
        _respuesta_archivo(archivo, tarea, id_usuario)
        for archivo in archivo_repository.obtener_archivos_de_tarea(db, id_tarea)
    ]


def obtener_archivo_para_descarga(
    db: Session, id_tarea: int, id_archivo: int, id_usuario: int
) -> tuple[Archivo, Path]:
    _autorizacion_tarea(db, id_tarea, id_usuario)
    archivo = archivo_repository.obtener_archivo_de_tarea(db, id_tarea, id_archivo)
    if archivo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    try:
        ruta = _resolver_ruta(archivo.ruta, id_tarea)
    except ValueError as error:
        logger.error("La ruta almacenada del adjunto %s no es válida", id_archivo)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado") from error
    except OSError as error:
        logger.exception("No se pudo acceder al almacenamiento del adjunto %s", id_archivo)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento no está disponible.",
        ) from error
    if not ruta.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
    return archivo, ruta


def eliminar_archivo_tarea(db: Session, id_tarea: int, id_archivo: int, id_usuario: int) -> None:
    tarea = _autorizacion_tarea(db, id_tarea, id_usuario)
    archivo = archivo_repository.obtener_archivo_de_tarea(db, id_tarea, id_archivo)
    if archivo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    puede_eliminar = tarea.id_usuario == id_usuario or archivo.id_usuario_subida == id_usuario
    if not puede_eliminar:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo quien subió este adjunto puede eliminarlo.",
        )

    try:
        otras_referencias = archivo_repository.existe_otra_referencia_a_ruta(
            db, archivo.ruta, id_archivo=archivo.id_archivo
        )
        ruta = _resolver_ruta(archivo.ruta, id_tarea)
        rutas = [] if otras_referencias else [ruta]
        with _archivos_en_cuarentena(rutas):
            try:
                archivo_repository.eliminar_archivo(db, archivo)
            except Exception as error:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo eliminar el adjunto.",
                ) from error
    except (OSError, ValueError) as error:
        logger.exception("No se pudo preparar el adjunto para su eliminación")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo acceder al almacenamiento del adjunto.",
        ) from error


@contextmanager
def preparar_eliminacion_archivos_tarea(db: Session, id_tarea: int) -> Iterator[None]:
    adjuntos = archivo_repository.obtener_archivos_de_tarea(db, id_tarea)
    rutas: list[Path] = []
    for adjunto in adjuntos:
        if archivo_repository.existe_referencia_fuera_de_tarea(db, adjunto.ruta, id_tarea):
            continue
        try:
            rutas.append(_resolver_ruta(adjunto.ruta, id_tarea))
        except ValueError as error:
            logger.error("La ruta almacenada del adjunto %s no es válida", adjunto.id_archivo)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo preparar el almacenamiento de los adjuntos de la tarea.",
            ) from error

    try:
        with _archivos_en_cuarentena(rutas):
            yield
    except OSError as error:
        logger.exception("No se pudieron preparar los adjuntos para eliminar la tarea")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento no está disponible.",
        ) from error
