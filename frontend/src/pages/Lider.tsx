import { useEffect, useState, useCallback } from 'react';
import { adminApi } from '../services/adminapi';
import { GenericTable } from '../components/admin/GenericTable';
import { FormularioModal } from '../components/admin/FormularioModal';
import { Resumen } from '../components/admin/Resumen';
import { TABS } from '../services/entidadesConfig';
import '../styles/lider.css';

// Tab especial que no es una entidad de la BD, solo la vista de resumen/gráfica
const TAB_RESUMEN = { clave: 'resumen', titulo: 'Resumen' };

// Lista completa de pestañas a mostrar (resumen + las entidades reales)
const TODAS_LAS_TABS = [TAB_RESUMEN, ...TABS];

export const Lider = () => {
    const [tabActivo, setTabActivo] = useState(TAB_RESUMEN.clave);
    const [filas, setFilas] = useState<any[]>([]);
    const [cargando, setCargando] = useState(false);
    const [guardando, setGuardando] = useState(false);
    const [modalAbierto, setModalAbierto] = useState(false);
    const [filaEditando, setFilaEditando] = useState<any | null>(null);
    const [error, setError] = useState<string | null>(null);
    const esTabResumen = tabActivo === TAB_RESUMEN.clave;
  // Solo buscamos la config de entidad si NO estamos en el tab de Resumen
    const configActual = esTabResumen ? null : TABS.find((t) => t.clave === tabActivo)!;

    const cargarDatos = useCallback(async () => {
    if (!configActual) return; // no hay nada que cargar en el tab de Resumen
    setCargando(true);
    setError(null);
    const datos = await adminApi.listar<any>(configActual.clave);
    if (datos === null) {
        setError('No se pudo cargar la información.');
        setFilas([]);
    } else {
        setFilas(datos);
    }
    setCargando(false);
    }, [configActual]);

    useEffect(() => {
    cargarDatos();
    }, [cargarDatos]);

    const abrirCrear = () => {
    setFilaEditando(null);
    setModalAbierto(true);
    };

    const abrirEditar = (fila: any) => {
    setFilaEditando(fila);
    setModalAbierto(true);
    };

    const guardar = async (datos: Record<string, unknown>) => {
    if (!configActual) return;
    setGuardando(true);
    const idField = Object.keys(configActual.valoresVacios).includes('id')
        ? 'id'
        : Object.keys(filaEditando ?? {}).find((k) => k.startsWith('id_') && filaEditando[k] !== undefined);

    const resultado = filaEditando
        ? await adminApi.actualizar(configActual.clave, filaEditando[idField!], datos)
        : await adminApi.crear(configActual.clave, datos);
    setGuardando(false);

    if (resultado === null) {
        setError('No se pudo guardar el registro.');
        return;
    }
    setModalAbierto(false);
    cargarDatos();
    };

    const eliminar = async (fila: any) => {
    const idField = Object.keys(fila).find((k) => k.startsWith('id_'));
    if (!confirm('¿Eliminar este registro?')) return;
    await adminApi.eliminar(configActual!.clave, fila[idField!]);
    cargarDatos();
    };

    return (
    <div className="admin-page">
        <h1>Panel de Administración — Acadex</h1>

        <div className="tabs">
        {TODAS_LAS_TABS.map((tab) => (
            <button
            key={tab.clave}
            className={`tab-btn ${tab.clave === tabActivo ? 'activo' : ''}`}
            onClick={() => setTabActivo(tab.clave)}
            >
            {tab.titulo}
            </button>
        ))}
        </div>

        {error && <p className="error-msg">{error}</p>}

        {esTabResumen ? (
        <Resumen />
        ) : (
        <>
            {!configActual!.soloLectura && (
            <div className="admin-toolbar">
                <button className="btn btn-primary" onClick={abrirCrear}>
                + Nuevo
                </button>
            </div>
            )}

            <GenericTable
            columnas={configActual!.columnas}
            filas={filas}
            cargando={cargando}
            soloLectura={configActual!.soloLectura}
            onEditar={abrirEditar}
            onEliminar={eliminar}
            />

            {!configActual!.soloLectura && (
            <FormularioModal
                titulo={filaEditando ? `Editar ${configActual!.titulo}` : `Nuevo ${configActual!.titulo}`}
                campos={configActual!.campos}
                valoresIniciales={filaEditando ?? configActual!.valoresVacios}
                abierto={modalAbierto}
                guardando={guardando}
                onCerrar={() => setModalAbierto(false)}
                onGuardar={guardar}
            />
            )}
        </>
        )}
    </div>
    );
};

export default Lider;