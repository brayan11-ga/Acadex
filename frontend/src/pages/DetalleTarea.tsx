import { useParams } from "react-router-dom";
import "../styles/detalleTarea.css";

function DetalleTarea() {

const { id } = useParams();

const tareas = [
    {
        id: 1,
        nombre: "Preparar presentación de Acadex",
        categoria: "Proyecto",
        fecha: "7 de septiembre",
        estado: "Pendiente",
    },
    {
        id: 2,
        nombre: "Terminar documentación",
        categoria: "Académica",
        fecha: "5 de septiembre",
        estado: "En progreso",
    },
    {
        id: 3,
        nombre: "Revisar pruebas del proyecto",
        categoria: "Desarrollo",
        fecha: "6 de septiembre",
        estado: "Completada",
    },
];

const tarea = tareas.find(
    (tarea) => tarea.id === Number(id)
);

return (
    <main className="detalle-tarea">

        {tarea ? (
            <div className="detalle-card">

                <h1>{tarea.nombre}</h1>

                <div className="detalle-info">
                    <p>
                        <strong>ID:</strong> {tarea.id}
                    </p>

                    <p>
                        <strong>Categoría:</strong> {tarea.categoria}
                    </p>

                    <p>
                        <strong>Fecha de entrega:</strong> {tarea.fecha}
                    </p>

                    <p>
                        <strong>Estado:</strong> {tarea.estado}
                    </p>
                </div>

            </div>
        ) : (
            <div className="detalle-card">
                <h1>Tarea no encontrada</h1>
                <p>No existe una tarea con el ID {id}.</p>
            </div>
        )}

    </main>
);

}

export default DetalleTarea;