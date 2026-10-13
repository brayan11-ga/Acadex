"""Acceso servidor a un bucket privado de Supabase Storage."""

from urllib.parse import quote, urlsplit

import httpx

from app.config.settings import settings


class SupabaseStorageError(RuntimeError):
    """Error de configuración o comunicación con el almacenamiento."""


class SupabaseObjectNotFound(SupabaseStorageError):
    """El objeto referenciado por la base de datos ya no existe en Storage."""


def _headers(content_type: str | None = None, *, upsert: bool = False) -> dict[str, str]:
    secret_key = getattr(settings, "supabase_secret_key", "").strip()
    legacy_service_role_key = getattr(settings, "supabase_service_role_key", "").strip()
    key = secret_key or legacy_service_role_key
    if not key:
        raise SupabaseStorageError("Supabase Storage no está configurado")
    headers = {"apikey": key}
    # Las claves nuevas sb_secret_* no son JWT: solo se envían como apikey.
    # La clave service_role antigua sí se envía también como Bearer para que
    # Storage la reconozca como la identidad privilegiada del backend.
    if not secret_key:
        headers["Authorization"] = f"Bearer {legacy_service_role_key}"
    if content_type:
        headers["Content-Type"] = content_type
    if upsert:
        headers["x-upsert"] = "true"
    return headers


def _base_url() -> str:
    base_url = settings.supabase_url.strip().rstrip("/")
    parsed = urlsplit(base_url)
    try:
        port = parsed.port
    except ValueError as error:
        raise SupabaseStorageError("SUPABASE_URL no es válida") from error
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or port is not None
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path
    ):
        raise SupabaseStorageError("Supabase Storage no está configurado con HTTPS")
    return base_url


def _url(bucket: str, object_key: str) -> str:
    base_url = _base_url()
    bucket_path = quote(bucket, safe="")
    object_path = "/".join(quote(segment, safe="") for segment in object_key.split("/"))
    return f"{base_url}/storage/v1/object/{bucket_path}/{object_path}"


def subir(bucket: str, object_key: str, contenido: bytes, content_type: str, *, upsert: bool = False) -> None:
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            respuesta = client.post(
                _url(bucket, object_key),
                content=contenido,
                headers=_headers(content_type, upsert=upsert),
            )
    except httpx.HTTPError as error:
        raise SupabaseStorageError("No se pudo contactar Supabase Storage") from error
    if not respuesta.is_success:
        raise SupabaseStorageError(f"Supabase Storage rechazó la subida (HTTP {respuesta.status_code})")


def descargar(bucket: str, object_key: str) -> bytes:
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            respuesta = client.get(_url(bucket, object_key), headers=_headers())
    except httpx.HTTPError as error:
        raise SupabaseStorageError("No se pudo contactar Supabase Storage") from error
    if respuesta.status_code == 404:
        raise SupabaseObjectNotFound("El objeto no existe en Supabase Storage")
    if not respuesta.is_success:
        raise SupabaseStorageError(f"Supabase Storage rechazó la descarga (HTTP {respuesta.status_code})")
    return respuesta.content


def eliminar(bucket: str, object_key: str) -> None:
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            respuesta = client.request(
                "DELETE",
                f"{_base_url()}/storage/v1/object/{quote(bucket, safe='')}",
                headers=_headers(),
                json={"prefixes": [object_key]},
            )
    except httpx.HTTPError as error:
        raise SupabaseStorageError("No se pudo contactar Supabase Storage") from error
    if not respuesta.is_success:
        raise SupabaseStorageError(f"Supabase Storage rechazó el borrado (HTTP {respuesta.status_code})")


def validar_bucket_privado() -> None:
    """Comprueba que el bucket configurado exista y no sea de acceso público."""
    bucket = settings.supabase_storage_bucket.strip()
    try:
        with httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            respuesta = client.get(
                f"{_base_url()}/storage/v1/bucket",
                headers=_headers(),
            )
    except httpx.HTTPError as error:
        raise SupabaseStorageError("No se pudo comprobar el bucket privado") from error
    if not respuesta.is_success:
        raise SupabaseStorageError("No se pudo comprobar el bucket privado")
    try:
        buckets = respuesta.json()
    except ValueError as error:
        raise SupabaseStorageError("Supabase Storage devolvió una respuesta no válida") from error
    if not isinstance(buckets, list):
        raise SupabaseStorageError("Supabase Storage devolvió una respuesta no válida")
    configurado = next(
        (item for item in buckets if isinstance(item, dict) and item.get("id") == bucket),
        None,
    )
    if configurado is None:
        raise SupabaseStorageError("El bucket configurado no existe")
    if configurado.get("public") is not False:
        raise SupabaseStorageError("El bucket de adjuntos debe ser privado")
