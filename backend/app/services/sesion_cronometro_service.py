# services/SesionCronometro_service
from datetime import datetime, timedelta ,timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.sesion_cronometro import SesionCronometro
from app.repositories import sesion_cronometro_repository as repo, tarea_repository, perfil_repository, notificacion_repository
from app.services import tarea_service

LIMITE_DEFECTO_SEG=1800 #limite por defecto 30min
GRACIA_MAX_SEG=60 #Tiempo maximo para responder antes de pausar solo

def _ahora()->datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _limite_segundos(perfil)->int:
    if perfil is not None and perfil.limite_cronometro:
        return perfil.limite_cronometro
    return LIMITE_DEFECTO_SEG

def _gracia_segundos(limite:int)->int:
    return min(GRACIA_MAX_SEG, limite//2)

def _notificar(db, perfil, id_usuario, id_tarea, titulo, detalles, tipo)->None:
    if perfil is not None and not perfil.notif_activas:
        return notificacion_repository.crear_notificacion(db, titulo[:50], detalles[:100], tipo, id_tarea
    )

def _estado(sesion, estado:str, limite:int, segundos_gracia:int | None=None)-> dict:
    return{"estado":estado,
            "limite_segundos":limite,
            "segundos_gracia_restantes":segundos_gracia,
            "sesion":sesion,
            }

def iniciar_sesion(db: Session, id_usuario: int, id_tarea: int) -> SesionCronometro:
    tarea=tarea_service.verificar_permiso_tarea(db, id_tarea, id_usuario, "cronometro")
    if repo.get_sesion_activa(db, id_tarea):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya hay una sesión activa para esta tarea",
        )
    data = {"fecha_inicio": _ahora(), "id_usuario": id_usuario, "id_tarea": id_tarea}
    tarea.cronometro_activo=True
    try:
        return repo.create_sesion(db, data)
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay una sesión activa para esta tarea",
        ) from None

def listar_sesiones_usuario(
    db: Session, id_usuario: int, id_usuario_actual: int) -> List[SesionCronometro]:
    if id_usuario != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron sesiones",
        )
    return repo.get_sesiones_by_usuario(db, id_usuario)


def _obtener_sesion_abierta(db: Session, id_sesion: int, id_usuario: int) -> SesionCronometro:
    sesion = repo.get_sesion_by_id(db, id_sesion)
    if not sesion or sesion.id_usuario !=id_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    if sesion.fecha_fin is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sesión ya fue cerrada",
        )
    return sesion

def obtener_estado_tarea(db:Session, id_tarea:int, id_usuario:int)-> dict:
    tarea=tarea_service.verificar_permiso_tarea(db, id_tarea, id_usuario, "cronometro")
    perfil =perfil_repository.get_perfil_by_usuario(db,id_usuario)
    sesion =repo.get_sesion_activa(db,id_tarea)
    if sesion is not None and sesion.id_usuario !=id_usuario:
        sesion=None
    en_curso=int((_ahora()-sesion.fecha_inicio).total_seconds()) if sesion else 0
    inicio=(Session.fecha_confirmacion or Session.fecha_inicio) if sesion else None
    ventana=int((_ahora()-inicio).total_seconds()) if inicio else 0
    return {"segundos_acumulados": int(round((tarea.tiempo_acumulado or 0) * 60)),
        "segundos_sesion_actual": max(0, en_curso),
        "segundos_ventana":max(0,ventana),
        "limite_segundos": _limite_segundos(perfil),
        "sesion": sesion,
        }

def _cerrar_sesion(db:Session,sesion:SesionCronometro, fecha_fin:datetime | None=None)->SesionCronometro:
    fecha_fin=fecha_fin or _ahora()
    duracion=(fecha_fin-sesion.fecha_inicio).total_seconds()
    tarea=tarea_repository.obtener_tarea_por_id(db, sesion.id_tarea)
    if tarea is not None:
        tarea.tiempo_acumulado=(tarea.tiempo_acumulado or 0)+ duracion /60 #min
        tarea.cronometro_activo=False
        tarea.ultima_pausa=fecha_fin
    return repo.update_sesion(db, sesion, {"fecha_fin":fecha_fin,"duracion":duracion})


def verificar_limite(db:int, id_sesion:int, id_usuario:int)->dict:
    sesion= repo.get_sesion_by_id(db,id_sesion)
    if not sesion or sesion.id_usuario !=id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no entrada")
    tarea=tarea_repository.obtener_tarea_por_id(db, sesion.id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    perfil=perfil_repository.get_perfil_by_usuario(db, id_usuario)
    limite=_limite_segundos(perfil)
    gracia=_gracia_segundos(limite)

    inicio_ventana=sesion.fecha_confirmacion or sesion.fecha_inicio
    momento_pausa=inicio_ventana+timedelta(seconds=limite)#pausa en el limite
    momento_aviso=momento_pausa- timedelta(seconds=gracia)#avisa antes der limite

    if sesion.fecha_fin is not None:
        auto=sesion.fecha_aviso is not None and sesion.fecha_fin ==momento_pausa
        return _estado(sesion, "pausada_automaticamente" if auto else "cerrada", limite)

    ahora=_ahora()

    if ahora>=momento_pausa:
        if sesion.fecha_aviso is None:
            sesion =repo.update_sesion(db, sesion,{"fecha_aviso":momento_aviso})
        sesion=_cerrar_sesion(db,sesion,momento_pausa)
        _notificar(db,perfil,id_usuario,tarea.id_tarea,"cronometro pausado", f"se pauso{tarea.nombre[:30]}por inactividad","cronometro_pausa_auto",)
        return _estado(sesion, "pausada_automaticamente", limite)

    if ahora>=momento_aviso:
        if sesion.fecha_aviso is None:
            sesion=repo.update_sesion(db,sesion,{"fecha_aviso":momento_aviso})
            _notificar(db,perfil,id_usuario, tarea.id_tarea,"¿sigues trabajando?", f"{tarea.nombre[:30]} se pausara pronto","cronometro_aviso")
        restante=max(0,int((momento_pausa-ahora).total_seconds()))
        return _estado(sesion, "aviso",limite,restante)
    return _estado(sesion,"activa",limite)


def confirmar_continuar(db:Session, id_sesion:int, id_usuario:int)->dict:
    estado=verificar_limite(db,id_sesion,id_usuario)
    if estado["estado"] !="aviso":
        return estado
    sesion=repo.update_sesion(
        db,estado["sesion"],{"fecha_confirmacion":_ahora(),"fecha_aviso":None}
    )
    return _estado(sesion,"activa", estado["limite_segundos"])


def pausar_sesion(db:Session, id_sesion:int, id_usuario:int)->SesionCronometro:
    return _cerrar_sesion(db, _obtener_sesion_abierta(db, id_sesion, id_usuario))

def finalizar_sesion(db:Session, id_sesion:int, id_usuario:int)->SesionCronometro:
    return _cerrar_sesion(db, _obtener_sesion_abierta(db, id_sesion, id_usuario))

def reiniciar_tarea(db:Session, id_tarea:int, id_usuario:int)->None:
    tarea = tarea_service.verificar_permiso_tarea(db, id_tarea, id_usuario, "cronometro")
    tarea.tiempo_acumulado=0
    tarea.cronometro_activo=False
    tarea.ultima_pausa=None
    repo.delete_sesiones_by_tarea(db, id_tarea)