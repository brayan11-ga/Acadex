import logging
import os
import re
import unicodedata
import uuid
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Iterator, List
from urllib.parse import urlsplit

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.archivo import Archivo
from app.services import supabase_storage
from app.repositories import (
    archivo_repository,
    asignacion_tarea_repository,
    grupo_repository,
    notificacion_repository,
    tarea_repository,
)

logger = logging.getLogger(__name__)


def _exigir_adjuntos_habilitados() -> None:
    if not settings.attachments_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Los adjuntos están desactivados mientras se configura almacenamiento persistente.",
        )

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


def _referencia_supabase(
    ruta_guardada: str, id_tarea_esperada: int | None = None
) -> tuple[str, str] | None:
    """Interpreta solo referencias internas seguras; nunca acepta una URL arbitraria."""
    parsed = urlsplit(ruta_guardada)
    if parsed.scheme != "supabase":
        return None
    if not parsed.netloc or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("La referencia de Supabase no es válida")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,62}", parsed.netloc):
        raise ValueError("El bucket de Supabase no es válido")
    bucket_configurado = getattr(settings, "supabase_storage_bucket", "").strip()
    if bucket_configurado and parsed.netloc != bucket_configurado:
        raise ValueError("La referencia apunta a un bucket no configurado")
    ruta_posix = PurePosixPath(parsed.path.lstrip("/"))
    if (
        ruta_posix.is_absolute()
        or not ruta_posix.parts
        or ".." in ruta_posix.parts
        or len(ruta_posix.parts) != 2
    ):
        raise ValueError("La clave de Supabase no es válida")
    if id_tarea_esperada is not None and ruta_posix.parts[0] != str(id_tarea_esperada):
        raise ValueError("La referencia no pertenece a la tarea solicitada")
    return parsed.netloc, "/".join(ruta_posix.parts)


def _ruta_supabase(bucket: str, object_key: str) -> str:
    return f"supabase://{bucket}/{object_key}"


def _almacenamiento_supabase() -> bool:
    return getattr(settings, "attachments_storage_backend", "local") == "supabase"


def _bytes_subida(archivo: UploadFile, tamano_esperado: int) -> bytes:
    try:
        contenido = archivo.file.read(TAMANO_MAXIMO_BYTES + 1)
    except OSError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo leer el archivo.",
        ) from error
    finally:
        archivo.file.seek(0)
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="El archivo supera el límite de 5MB.",
        )
    if len(contenido) != tamano_esperado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo leer el archivo completo.")
    return contenido


@contextmanager
def _objetos_supabase_en_cuarentena(
    objetos: list[tuple[str, str, str]],
) -> Iterator[None]:
    """Borra objetos privados y los restaura si falla la transacción PostgreSQL."""
    respaldos: dict[tuple[str, str, str], bytes] = {}
    intentados: list[tuple[str, str, str]] = []
    unicos = list(dict.fromkeys(objetos))
    try:
        for bucket, object_key, content_type in unicos:
            contenido = supabase_storage.descargar(bucket, object_key)
            respaldos[(bucket, object_key, content_type)] = contenido
            intentados.append((bucket, object_key, content_type))
            supabase_storage.eliminar(bucket, object_key)
        yield
    except BaseException:
        for objeto in reversed(intentados):
            bucket, object_key, content_type = objeto
            try:
                supabase_storage.subir(
                    bucket,
                    object_key,
                    respaldos[objeto],
                    content_type,
                    upsert=True,
                )
            except supabase_storage.SupabaseStorageError:
                logger.exception("No se pudo restaurar un adjunto privado tras fallar PostgreSQL")
        raise


@contextmanager
def compensar_subidas_adjuntos() -> Iterator[list[tuple]]:
    """Retira los binarios si no llega a confirmarse la transacción PostgreSQL."""
    recursos: list[tuple] = []
    try:
        yield recursos
    except BaseException:
        for recurso in reversed(recursos):
            try:
                if recurso[0] == "supabase":
                    _, bucket, object_key = recurso
                    supabase_storage.eliminar(bucket, object_key)
                else:
                    _, ruta = recurso
                    _quitar_binario_si_huerfano(ruta)
            except supabase_storage.SupabaseStorageError:
                logger.exception("No se pudo retirar un objeto privado tras cancelar el guardado")
        raise


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

def _autorizacion_lectura_tarea(db: Session, id_tarea: int, id_usuario: int):
    """Permiso para VER y DESCARGAR adjuntos: dueño (individual) o miembro del grupo (grupal)."""
    # Import local para evitar un posible import circular con tarea_service.
    from app.services import tarea_service

    # Devuelve el modelo Tarea. Lanza 404 si no existe y 403 si no eres
    # dueño ni miembro del grupo: la misma regla que usa /asignados, definida
    # en un solo lugar para que no vuelva a quedar una copia desactualizada.
    return tarea_service.obtener_tarea(db, id_tarea, id_usuario)


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


def subir_archivo_tarea(
    db: Session,
    id_tarea: int,
    archivo: UploadFile,
    id_usuario: int,
    *,
    commit: bool = True,
    recursos_creados: list[tuple] | None = None,
) -> dict:
    _exigir_adjuntos_habilitados()
    tarea = _autorizacion_tarea(db, id_tarea, id_usuario)
    total_archivos = archivo_repository.contar_archivos_de_tarea(db, id_tarea)
    if total_archivos >= tarea.max_archivos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Esta tarea ya alcanzó el máximo de {tarea.max_archivos} archivos.",
        )
    nombre, tipo, tamano = _validar_archivo(archivo)
    extension = Path(nombre).suffix.lower()
    ruta_fisica: Path | None = None
    objeto_supabase: tuple[str, str] | None = None
    try:
        if _almacenamiento_supabase():
            contenido = _bytes_subida(archivo, tamano)
            bucket = settings.supabase_storage_bucket.strip()
            object_key = f"{id_tarea}/{uuid.uuid4().hex}{extension}"
            supabase_storage.subir(bucket, object_key, contenido, TIPOS_MIME[tipo])
            objeto_supabase = (bucket, object_key)
            if recursos_creados is not None:
                recursos_creados.append(("supabase", bucket, object_key))
            ruta_relativa = _ruta_supabase(bucket, object_key)
        else:
            ruta_fisica, ruta_relativa = _guardar_binario(archivo, id_tarea, extension, tamano)
            if recursos_creados is not None:
                recursos_creados.append(("local", ruta_fisica))
    except HTTPException:
        raise
    except (OSError, supabase_storage.SupabaseStorageError) as error:
        logger.warning("El almacenamiento no pudo completar la subida (%s)", type(error).__name__)
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
            commit=commit,
        )
    except Exception as error:
        if commit:
            db.rollback()
        if recursos_creados is None and objeto_supabase is not None:
            try:
                supabase_storage.eliminar(*objeto_supabase)
            except supabase_storage.SupabaseStorageError:
                logger.exception("No se pudo retirar el objeto privado tras fallar PostgreSQL")
        elif recursos_creados is None and ruta_fisica is not None:
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
    _exigir_adjuntos_habilitados()
    tarea = _autorizacion_lectura_tarea(db, id_tarea, id_usuario)  # antes: _autorizacion_tarea
    return [
        _respuesta_archivo(archivo, tarea, id_usuario)
        for archivo in archivo_repository.obtener_archivos_de_tarea(db, id_tarea)
    ]


def obtener_archivo_para_descarga(
    db: Session, id_tarea: int, id_archivo: int, id_usuario: int
) -> tuple[Archivo, Path | bytes]:
    _exigir_adjuntos_habilitados()
    _autorizacion_lectura_tarea(db, id_tarea, id_usuario)
    archivo = archivo_repository.obtener_archivo_de_tarea(db, id_tarea, id_archivo)
    if archivo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    try:
        referencia = _referencia_supabase(archivo.ruta, id_tarea)
        if referencia is not None:
            contenido = supabase_storage.descargar(*referencia)
            return archivo, contenido
        ruta = _resolver_ruta(archivo.ruta, id_tarea)
    except ValueError as error:
        logger.error("La ruta almacenada del adjunto %s no es válida", id_archivo)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado") from error
    except supabase_storage.SupabaseObjectNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado") from error
    except supabase_storage.SupabaseStorageError as error:
        logger.warning("Supabase Storage no pudo entregar el adjunto %s", id_archivo)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento no está disponible.",
        ) from error
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
    _exigir_adjuntos_habilitados()
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
        referencia = _referencia_supabase(archivo.ruta, id_tarea)
        rutas = []
        objetos = []
        if not otras_referencias:
            if referencia is not None:
                objetos.append((*referencia, TIPOS_MIME[archivo.tipo]))
            else:
                rutas.append(_resolver_ruta(archivo.ruta, id_tarea))
        with _archivos_en_cuarentena(rutas), _objetos_supabase_en_cuarentena(objetos):
            try:
                archivo_repository.eliminar_archivo(db, archivo)
            except Exception as error:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo eliminar el adjunto.",
                ) from error
    except supabase_storage.SupabaseStorageError as error:
        logger.warning("Supabase Storage no pudo preparar la eliminación del adjunto %s", id_archivo)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo acceder al almacenamiento del adjunto.",
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
    objetos: list[tuple[str, str, str]] = []
    for adjunto in adjuntos:
        if archivo_repository.existe_referencia_fuera_de_tarea(db, adjunto.ruta, id_tarea):
            continue
        try:
            referencia = _referencia_supabase(adjunto.ruta, id_tarea)
            if referencia is not None:
                objetos.append((*referencia, TIPOS_MIME[adjunto.tipo]))
            else:
                rutas.append(_resolver_ruta(adjunto.ruta, id_tarea))
        except ValueError as error:
            logger.error("La ruta almacenada del adjunto %s no es válida", adjunto.id_archivo)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo preparar el almacenamiento de los adjuntos de la tarea.",
            ) from error

    try:
        # La tarea y sus filas ya quedan protegidas por la transacción de PostgreSQL.
        # Los objetos remotos se borran después del commit para no cargar todos sus
        # binarios en memoria; si Storage no responde, permanecen privados y huérfanos.
        with _archivos_en_cuarentena(rutas):
            yield
        for bucket, object_key, _content_type in dict.fromkeys(objetos):
            try:
                supabase_storage.eliminar(bucket, object_key)
            except supabase_storage.SupabaseStorageError:
                logger.exception(
                    "No se pudo limpiar un objeto privado después de eliminar la tarea %s",
                    id_tarea,
                )
    except OSError as error:
        logger.exception("No se pudieron preparar los adjuntos para eliminar la tarea")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El almacenamiento no está disponible.",
        ) from error


@contextmanager
def preparar_eliminacion_archivos_usuarios_tarea(
    db: Session, id_tarea: int, ids_usuarios: list[int]
) -> Iterator[None]:
    """Cuarentena tolerante de los adjuntos de varios usuarios (C4c).

    A diferencia de preparar_eliminacion_archivos_tarea, un fallo del
    almacenamiento no lanza: se registra en el log y la reasignación continúa.
    Si falla la transacción de PostgreSQL, los binarios locales movidos se
    restauran para no perderlos.
    """
    adjuntos = archivo_repository.obtener_archivos_de_usuarios_en_tarea(
        db, id_tarea, ids_usuarios
    )
    rutas: list[Path] = []
    objetos: list[tuple[str, str, str]] = []
    for adjunto in adjuntos:
        if archivo_repository.existe_referencia_fuera_de_tarea(
            db, adjunto.ruta, id_tarea
        ):
            continue
        try:
            referencia = _referencia_supabase(adjunto.ruta, id_tarea)
            if referencia is not None:
                objetos.append((*referencia, TIPOS_MIME[adjunto.tipo]))
            else:
                rutas.append(_resolver_ruta(adjunto.ruta, id_tarea))
        except (ValueError, OSError):
            logger.exception(
                "No se pudo preparar el adjunto %s para eliminarlo al reasignar",
                adjunto.id_archivo,
            )

    movidos: list[tuple[Path, Path]] = []
    for ruta in {ruta.resolve() for ruta in rutas}:
        try:
            if not ruta.exists():
                continue
            if not ruta.is_file():
                logger.warning(
                    "La ruta %s no es un archivo; se omite al reasignar", ruta
                )
                continue
            temporal = ruta.with_name(f".{ruta.name}.{uuid.uuid4().hex}.deleting")
            os.replace(ruta, temporal)
            movidos.append((ruta, temporal))
        except OSError:
            logger.exception(
                "No se pudo mover a cuarentena el adjunto %s al reasignar", ruta
            )

    try:
        yield
    except BaseException:
        for original, temporal in reversed(movidos):
            try:
                if temporal.exists():
                    os.replace(temporal, original)
            except OSError:
                logger.exception(
                    "No se pudo restaurar un adjunto tras fallar la reasignación"
                )
        raise
    else:
        for _, temporal in movidos:
            try:
                temporal.unlink(missing_ok=True)
            except OSError:
                logger.exception("No se pudo retirar el binario en cuarentena")
        for bucket, object_key, _content_type in dict.fromkeys(objetos):
            try:
                supabase_storage.eliminar(bucket, object_key)
            except Exception:
                # La reasignación ya está confirmada: cualquier fallo de Storage
                # se registra y no se propaga.
                logger.exception(
                    "No se pudo borrar un objeto privado tras reasignar la tarea %s",
                    id_tarea,
                )
