import type { ColumnConfig } from './Types';
interface GenericTableProps<T> {
    columnas: ColumnConfig<T>[];
    filas: T[];
    cargando?: boolean;
    soloLectura?: boolean;
    onEditar?: (fila: T) => void;
    onEliminar?: (fila: T) => void;
}

export function GenericTable<T extends Record<string, any>>({
    columnas,
    filas,
    cargando = false,
    soloLectura = false,
    onEditar,
    onEliminar,
}: GenericTableProps<T>) {
    if (cargando) return <p>Cargando...</p>;
    if (filas.length === 0) return <p>No hay registros.</p>;

    return (
    <table className="tabla-admin">
        <thead>
        <tr>
            {columnas.map((col) => (
            <th key={String(col.key)}>{col.label}</th>
            ))}
            {!soloLectura && <th>Acciones</th>}
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
            {!soloLectura && (
                <td>
                <button className="btn btn-secundario" onClick={() => onEditar?.(fila)}>
                    Editar
                </button>
                <button className="btn btn-peligro" onClick={() => onEliminar?.(fila)}>
                    Eliminar
                </button>
                </td>
            )}
            </tr>
        ))}
        </tbody>
    </table>
    );
}

export default GenericTable;