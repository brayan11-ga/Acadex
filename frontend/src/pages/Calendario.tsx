import React, { useState } from 'react';
import '../styles/calendario.css';

interface Evento {
  id: number;
  titulo: string;
  fecha: string; // Formato YYYY-MM-DD
  prioridad: 'baja' | 'media' | 'alta';
}

// Datos simulados (mock) para probar la vista
const EVENTOS_SIMULADOS: Evento[] = [
  { id: 1, titulo: 'Entregar Avance de Acadex', fecha: '2026-09-10', prioridad: 'alta' },
  { id: 2, titulo: 'Reunión de Feedback SENA', fecha: '2026-09-15', prioridad: 'media' },
  { id: 3, titulo: 'Pruebas No Funcionales', fecha: '2026-09-20', prioridad: 'baja' },
];

export const Calendario: React.FC = () => {
  const [fechaActual, setFechaActual] = useState(new Date());

  const año = fechaActual.getFullYear();
  const mes = fechaActual.getMonth();

  // Nombres de meses y días en español
  const meses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];
  const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  // Obtener primer y último día del mes
  const primerDiaMes = new Date(año, mes, 1).getDay();
  const totalDiasMes = new Date(año, mes + 1, 0).getDate();

  // Navegación entre meses
  const mesAnterior = () => setFechaActual(new Date(año, mes - 1, 1));
  const mesSiguiente = () => setFechaActual(new Date(año, mes + 1, 1));

  // Renderizar las celdas del calendario
  const renderDias = () => {
    const celdas = [];

    // Celdas vacías antes del primer día del mes
    for (let i = 0; i < primerDiaMes; i++) {
      celdas.push(<div key={`empty-${i}`} className="dia-celda vacia"></div>);
    }

    // Días del mes
    for (let dia = 1; dia <= totalDiasMes; dia++) {
      const fechaString = `${año}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
      const eventosDelDia = EVENTOS_SIMULADOS.filter((e) => e.fecha === fechaString);
      const esHoy = new Date().toDateString() === new Date(año, mes, dia).toDateString();

      celdas.push(
        <div key={dia} className={`dia-celda ${esHoy ? 'hoy' : ''}`}>
          <span className="numero-dia">{dia}</span>
          <div className="lista-eventos">
            {eventosDelDia.map((evt) => (
              <div key={evt.id} className={`evento-badge prioridad-${evt.prioridad}`}>
                {evt.titulo}
              </div>
            ))}
          </div>
        </div>
      );
    }

    return celdas;
  };

  return (
    <div className="calendario-container">
      <header className="calendario-header">
        <h2>{meses[mes]} {año}</h2>
        <div className="calendario-controles">
          <button onClick={mesAnterior}>&lt; Anterior</button>
          <button onClick={() => setFechaActual(new Date())}>Hoy</button>
          <button onClick={mesSiguiente}>Siguiente &gt;</button>
        </div>
      </header>

      <div className="calendario-grid">
        {diasSemana.map((dia) => (
          <div key={dia} className="encabezado-dia">{dia}</div>
        ))}
        {renderDias()}
      </div>
    </div>
  );
};

export default Calendario;