// pageAdmin
import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../services/adminapi';
import { GenericTable } from '../components/admin/GenericTable';
import { Resumen } from '../components/admin/Resumen';
import { Sidebar} from '../components/admin/Sidebar';
import { TABS_ADMIN } from '../services/entidadesConfig';
import { usePerfilActual } from '../hooks/usePerfilActual';
import '../styles/admin.css';

const TAB_RESUMEN = { clave: 'resumen', titulo: 'Resumen' };
const TODAS_LAS_TABS = [TAB_RESUMEN, ...TABS_ADMIN];

export const Admin = () => {
    const [tabActivo, setTabActivo] = useState(TAB_RESUMEN.clave);
    const [filas, setFilas] = useState<any[]>([]);
    const [cargando, setCargando] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [errorCarga, setErrorCarga] = useState<string | null>(null);
    const { perfil } = usePerfilActual();
    const esTabResumen = tabActivo === TAB_RESUMEN.clave;
    const configActual = esTabResumen ? null : TABS_ADMIN.find((t) => t.clave === tabActivo)!;

    const cargarDatos = useCallback(async () => {
    if (!configActual) return;
    setCargando(true);
    setErrorCarga(null);
    setError(null);
    const datos = await adminApi.listar<any>(configActual.clave);
    if (datos === null) {
        setErrorCarga('No se pudo cargar la información.');
        setFilas([]);
    } else {
        setFilas(datos);
    }
    setCargando(false);
    }, [configActual]);

    useEffect(() => {
    cargarDatos();
    }, [cargarDatos]);

    const eliminar = async (fila: any) => {
    const idField = Object.keys(fila).find((k) => k.startsWith('id_'));
    if (!confirm('¿Eliminar este registro?')) return;
    await adminApi.eliminar(configActual!.clave, fila[idField!]);
    cargarDatos();
    };

    //  generar contraseña haseada aleatoria
const restablecerPassword = async (fila: any) => {
    const idField = Object.keys(fila).find((k) => k.startsWith('id_'));
    if (!confirm(`¿Restablecer la contraseña de ${fila.correo_electronico ?? 'este usuario'}?`)) return;

    const resultado = await adminApi.restablecerPassword<{ valor_token: string; fecha_expiracion: string }>(fila[idField!]);
    if (resultado === null) {
    setError('No se pudo restablecer la contraseña.');
    return;
    }

    window.prompt(
        `Token temporal de recuperación. Vence: ${new Date(resultado.fecha_expiracion).toLocaleString()}. Envíalo solo al usuario por un canal seguro.`,
        resultado.valor_token,
    );
};

    return (
        <div className="admin-page">
        <Sidebar
            tabs={TODAS_LAS_TABS}
            tabActivo={tabActivo}
            onCambiarTab={(clave) => {
                setTabActivo(clave);
                setErrorCarga(null);
                setCargando(clave !== TAB_RESUMEN.clave);
            }}
        />

        <main className="admin-content">
            <h1>Panel de Administración — Acadex</h1>
            <p className="admin-welcome">
                {'¡Te damos la bienvenida a Acadex' +
                  (perfil?.nombre_usuario?.trim() ? ', ' + perfil.nombre_usuario.trim() : '') +
                  '!'}
            </p>

            {error && <p className="error-msg">{error}</p>}

            {esTabResumen ? (
            <Resumen />
            ) : (
            <>
                {errorCarga ? (
                    <div className="error-msg" role="alert">
                        <p>{errorCarga}</p>
                        <button type="button" className="btn btn-secundario" onClick={() => void cargarDatos()}>
                            Reintentar
                        </button>
                    </div>
                ) : (
                    <GenericTable
                    columnas={configActual!.columnas}
                    filas={filas}
                    cargando={cargando}
                    soloLectura={configActual!.soloLectura}
                    emptyState={configActual!.emptyState}
                    onEliminar={configActual!.clave === 'usuarios' ? eliminar : undefined}
                    accionesExtra={
                        configActual!.clave === 'usuarios'
                        ? [{ etiqueta: 'Restablecer contraseña', onClick: restablecerPassword, claseCss: 'btn btn-secundario' }]
                        : []
                    }
                    />
                )}

            </>
            )}
        </main>
        </div>
    );
};

export default Admin;
