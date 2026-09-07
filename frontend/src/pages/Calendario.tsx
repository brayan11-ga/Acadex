import React, { useState, useEffect } from 'react';
import { obtenerTareasCalendario, type TareaBackend } from '../services/tareas';
import '../styles/calendario.css';

export const Calendario: React.FC = () => {
  const [fechaActual, setFechaActual] = useState(new Date());
  const [tareas, setTareas] = useState<TareaBackend[]>([]);
  const [cargando, setCargando] = useState(false);

  const año = fechaActual.getFullYear();
  const mes = fechaActual.getMonth();

  const meses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];
  const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  const primerDiaMes = new Date(año, mes, 1).getDay();
  const totalDiasMes = new Date(año, mes + 1, 0).getDate();

  useEffect(() => {
    const cargarTareas = async () => {
      setCargando(true);
      try {
        const fechaInicio = `${año}-${String(mes + 1).padStart(2, '0')}-01`;
        const fechaFin = `${año}-${String(mes + 1).padStart(2, '0')}-${totalDiasMes}`;

        const data = await obtenerTareasCalendario(fechaInicio, fechaFin);
        setTareas(data);
      } catch (error) {
        console.error('Error al cargar tareas del calendario:', error);
      } finally {
        setCargando(false);
      }
    };

    cargarTareas();
  }, [año, mes, totalDiasMes]);

  const mesAnterior = () => setFechaActual(new Date(año, mes - 1, 1));
  const mesSiguiente = () => setFechaActual(new Date(año, mes + 1, 1));
  const añoAnterior = () => setFechaActual(new Date(año - 1, mes, 1));
  const añoSiguiente = () => setFechaActual(new Date(año + 1, mes, 1));
  const irHoy = () => setFechaActual(new Date());

  const renderDias = () => {
    const celdas = [];

    for (let i = 0; i < primerDiaMes; i++) {
      celdas.push(<div key={`vacia-${i}`} className="dia-celda vacia"></div>);
    }

    for (let dia = 1; dia <= totalDiasMes; dia++) {
      const fechaString = `${año}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;

      const tareasDelDia = tareas.filter((t) => {
        if (!t.fecha_entrega) return false;
        return t.fecha_entrega.split('T')[0] === fechaString;
      });

      const esHoy = new Date().toDateString() === new Date(año, mes, dia).toDateString();

      celdas.push(
        <div key={dia} className={`dia-celda ${esHoy ? 'hoy' : ''}`}>
          <span className="numero-dia">{dia}</span>
          <div className="lista-eventos">
            {tareasDelDia.map((t) => (
              <div
                key={t.id_tarea}
                className={`evento-badge estado-${t.estado}`}
                title={`${t.nombre} (${t.estado.replace('_', ' ')})`}
              >
                {t.nombre}
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
        <h2>
          {meses[mes]} {año}{' '}
          {cargando && <small style={{ fontSize: '0.8rem', color: '#a5b4fc' }}>(Cargando...)</small>}
        </h2>
        <div className="calendario-controles">
          <button onClick={añoAnterior}>&lt;&lt; Año</button>
          <button onClick={mesAnterior}>&lt; Mes</button>
          <button onClick={irHoy}>Hoy</button>
          <button onClick={mesSiguiente}>Mes &gt;</button>
          <button onClick={añoSiguiente}>Año &gt;&gt;</button>
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