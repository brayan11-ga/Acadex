import type { ColumnConfig } from './Types';
import { AdminTableLoadingSkeleton } from '../skeletons/LoadingSkeletons';
import { EmptyState } from '../ui/EmptyState';

interface AccionExtra<T> {
    etiqueta: string;
    onClick: (fila: T) => void;
    claseCss?: string;
}

interface GenericTableProps<T> {
    columnas: ColumnConfig<T>[];
    filas: T[];
    cargando?: boolean;
    soloLectura?: boolean;
    emptyState?: { title: string; description: string };
    onEditar?: (fila: T) => void;
    onEliminar?: (fila: T) => void;
    accionesExtra?: AccionExtra<T>[]; // <-- nuevo
}

export function GenericTable<T extends Record<string, any>>({
    columnas,
    filas,
    cargando = false,
    soloLectura = false,
    emptyState,
    onEditar,
    onEliminar,
    accionesExtra = [],
}: GenericTableProps<T>) {
    const mostrarAcciones = !soloLectura && Boolean(onEditar || onEliminar || accionesExtra.length);

    if (cargando) {
        return (
            <AdminTableLoadingSkeleton
                columns={columnas.map((columna) => columna.label)}
                hasActions={mostrarAcciones}
            />
        );
    }
    if (filas.length === 0) {
        return (
            <EmptyState
                className="empty-state--compact"
                title={emptyState?.title ?? 'Aún no hay registros'}
                description={emptyState?.description ?? 'Cuando haya datos, aparecerán aquí.'}
            />
        );
    }

    return (
    <table className="tabla-admin">
        <thead>
        <tr>
            {columnas.map((col) => (
            <th key={String(col.key)}>{col.label}</th>
            ))}
            {mostrarAcciones && <th>Acciones</th>}
        </tr>
        </thead>
        <tbody>
        {filas.map((fila, i) => (
            <tr key={i}>
            {columnas.map((col) => (
                <td key={String(col.key)}>
                {col.render ? col.render(fila) : String(fila[col.key] ?? '')}
                </td>
            ))}
            {mostrarAcciones && (
                <td>
                {onEditar && <button className="btn btn-secundario" onClick={() => onEditar(fila)}>
                    Editar
                </button>}
                {onEliminar && <button className="btn btn-peligro" onClick={() => onEliminar(fila)}>
                    Eliminar
                </button>}
                {accionesExtra.map((accion) => (
                    <button
                    key={accion.etiqueta}
                    className={accion.claseCss ?? 'btn btn-secundario'}
                    onClick={() => accion.onClick(fila)}
                    >
                    {accion.etiqueta}
                    </button>
                ))}
                </td>
            )}
            </tr>
        ))}
        </tbody>
    </table>
    );
}

export default GenericTable;
