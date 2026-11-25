# prioridad_repositorio
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea

def _alcance_tarea(id_usuario,id_grupo):
    if id_grupo is not None:
        return [Tarea.id_grupo==id_grupo]
    return [Tarea.id_usuario==id_usuario,Tarea.id_grupo.is_(None)]

def _alcance_historial(id_usuario, id_grupo):
    if id_grupo is not None:
        return [HistorialTarea.id_grupo==id_grupo]
    return [HistorialTarea.id_usuario==id_usuario,HistorialTarea.id_grupo.is_(None)]

def contar_tareas(db:Session, id_usaurio,id_grupo, excluir_id:int)->int:
    return(db.query(func.count(Tarea.id_tarea)).filter(*_alcance_tarea(id_usaurio,id_grupo), Tarea.id_tarea !=excluir_id).scalar())

def obtener_historial(db:Session,id_categoria,id_usaurio,id_grupo,limite:int=10)->list[dict]:
    if id_grupo is not None:
        return _historial_grupal(db, id_categoria, id_grupo, limite)
    filas=(db.query(Tarea.tiempo_estimado,Tarea.dificultad_estimada,HistorialTarea.tiempo_real,HistorialTarea.dificultad_real)
        .join(Tarea,Tarea.id_tarea==HistorialTarea.id_tarea)
        .filter(Tarea.id_categoria==id_categoria,HistorialTarea.tiempo_real.isnot(None),*_alcance_historial(id_usaurio, id_grupo))
        .order_by(HistorialTarea.fechahora_fin.desc())
        .limit(limite)
        .all()
    )
    return[{"tiempo_estimado":f[0],"dificultad_estimada":f[1],"tiempo_real":f[2],"dificultad_real":f[3],} for f in filas]

def _historial_grupal(db:Session, id_categoria, id_grupo, limite:int)->list[dict]:
    ultimo_fin=func.max(HistorialTarea.fechahora_fin)
    filas=(
        db.query(Tarea.tiempo_estimado, Tarea.dificultad_estimada,
                func.avg(HistorialTarea.tiempo_real),
                func.avg(HistorialTarea.dificultad_real))
            .join(Tarea, Tarea.id_tarea==HistorialTarea.id_tarea)
            .filter(Tarea.id_categoria==id_categoria,
                    HistorialTarea.tiempo_real.isnot(None),
                    HistorialTarea.id_grupo==id_grupo)
                .group_by(Tarea.id_tarea, Tarea.tiempo_estimado, Tarea.dificultad_estimada)
                .order_by(ultimo_fin.desc())
                .limit(limite)
                .all()
    )
    return [{"tiempo_estimado": f[0],"dificultad_estimada":f[1],
            "dificultad_real":float(f[2]),
            "dificultad_real":float(f[3])if f[3] is not None else None}
            for f in filas]

def obtener_pendientes(db:Session,id_categoria,id_usuario,id_grupo)->list[Tarea]:
    return (db.query(Tarea).filter(Tarea.id_categoria==id_categoria,func.lower(Tarea.estado)!="completada",*_alcance_tarea(id_usuario,id_grupo),).all())
