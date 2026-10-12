from threading import Lock
from time import monotonic

from fastapi import HTTPException, status

VENTANA_SEGUNDOS = 15 * 60
MAX_INTENTOS = 5
MAX_CLIENTES = 10_000

_intentos: dict[str, tuple[float, int]] = {}
_bloqueo = Lock()


def registrar_intento(identificador_cliente: str) -> None:
    ahora = monotonic()
    cliente = identificador_cliente or "desconocido"

    with _bloqueo:
        expirados = [
            clave for clave, (inicio, _) in _intentos.items()
            if ahora - inicio >= VENTANA_SEGUNDOS
        ]
        for clave in expirados:
            _intentos.pop(clave, None)

        inicio, cantidad = _intentos.get(cliente, (ahora, 0))
        if ahora - inicio >= VENTANA_SEGUNDOS:
            inicio, cantidad = ahora, 0
        if cantidad >= MAX_INTENTOS:
            espera = max(1, int(VENTANA_SEGUNDOS - (ahora - inicio)))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Has intentado registrarte varias veces. Espera unos minutos e inténtalo de nuevo.",
                headers={"Retry-After": str(espera)},
            )

        if len(_intentos) >= MAX_CLIENTES and cliente not in _intentos:
            cliente_mas_antiguo = min(_intentos, key=lambda clave: _intentos[clave][0])
            _intentos.pop(cliente_mas_antiguo, None)
        _intentos[cliente] = (inicio, cantidad + 1)
