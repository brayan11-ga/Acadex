from sqlalchemy.orm import Session
from app.models.perfil import Perfil
from app.models.estadistica_categoria import EstadisticaCategoria
from app.models.categoria import Categoria
from sqlalchemy import func
from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea

def obtener_estadisticas_categoria_usuario(db: Session, id_usuario: int):
    perfil = db.query(Perfil).filter(Perfil.id_usuario == id_usuario).first()

    if not perfil:
        return []

    resultados = (
        db.query(
            Categoria.nombre_categoria,
            EstadisticaCategoria.promedio_tiempo,
            EstadisticaCategoria.promedio_dificultad,
            EstadisticaCategoria.total_tareas,
        )
        .join(Categoria, Categoria.id_categoria == EstadisticaCategoria.id_categoria)
        .filter(EstadisticaCategoria.id_perfil == perfil.id_perfil)
        .all()
    )

    return [
        {
            "nombre_categoria": r.nombre_categoria,
            "promedio_tiempo": r.promedio_tiempo,
            "promedio_dificultad": r.promedio_dificultad,
            "total_tareas": r.total_tareas,
        }
        for r in resultados
    ]


def recalcular_estadistica_categoria(db: Session, id_usuario: int, id_categoria: int) -> None:
    perfil = db.query(Perfil).filter(Perfil.id_usuario == id_usuario).first()
    if not perfil:
        return

    agregado = (
        db.query(
            func.avg(HistorialTarea.tiempo_real),
            func.avg(HistorialTarea.dificultad_real),
            func.count(HistorialTarea.id_historial),
        )
        .join(Tarea, Tarea.id_tarea == HistorialTarea.id_tarea)
        .filter(
            HistorialTarea.id_usuario == id_usuario,
            Tarea.id_categoria == id_categoria,
        )
        .first()
    )

    promedio_tiempo, promedio_dificultad, total = agregado

    estadistica = (
        db.query(EstadisticaCategoria)
        .filter(
            EstadisticaCategoria.id_perfil == perfil.id_perfil,
            EstadisticaCategoria.id_categoria == id_categoria,
        )
        .first()
    )

    if total == 0:
        if estadistica:
            db.delete(estadistica)
            db.commit()
        return

    if estadistica:
        estadistica.promedio_tiempo = promedio_tiempo
        estadistica.promedio_dificultad = promedio_dificultad
        estadistica.total_tareas = total
    else:
        estadistica = EstadisticaCategoria(
            id_perfil=perfil.id_perfil,
            id_categoria=id_categoria,
            promedio_tiempo=promedio_tiempo,
            promedio_dificultad=promedio_dificultad,
            total_tareas=total,
        )
        db.add(estadistica)

    db.commit()