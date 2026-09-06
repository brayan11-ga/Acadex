from sqlalchemy.orm import Session
from app.models.perfil import Perfil
from app.models.estadistica_categoria import EstadisticaCategoria
from app.models.categoria import Categoria  # ajusta el nombre si tu modelo se llama distinto

def obtener_estadisticas_categoria_usuario(db: Session, id_usuario: int):
    # 1. Buscamos el perfil del usuario (1 a 1 con usuarios)
    perfil = db.query(Perfil).filter(Perfil.id_usuario == id_usuario).first()

    if not perfil:
        # Si por algún motivo no tiene perfil, devolvemos lista vacía en vez de error
        return []

    # 2. Traemos las estadísticas por categoría de ESE perfil, con el nombre de la categoría
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

    # 3. Convertimos cada fila (tupla) a un diccionario para que el schema lo pueda leer
    return [
        {
            "nombre_categoria": r.nombre_categoria,
            "promedio_tiempo": r.promedio_tiempo,
            "promedio_dificultad": r.promedio_dificultad,
            "total_tareas": r.total_tareas,
        }
        for r in resultados
    ]