import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import type { FieldConfig } from './Types';
import { adminApi } from '../../services/adminapi';

interface FormularioModalProps {
    titulo: string;
    campos: FieldConfig[];
    valoresIniciales: Record<string, unknown>;
    abierto: boolean;
    guardando?: boolean;
    onCerrar: () => void;
    onGuardar: (datos: Record<string, unknown>) => void;
}

export const FormularioModal = ({
    titulo,
    campos,
    valoresIniciales,
    abierto,
    guardando = false,
    onCerrar,
    onGuardar,
}: FormularioModalProps) => {
    const [valores, setValores] = useState<Record<string, unknown>>(valoresIniciales);
    const [opcionesDinamicas, setOpcionesDinamicas] = useState<Record<string, any[]>>({});

    useEffect(() => {
    setValores(valoresIniciales);
    }, [valoresIniciales, abierto]);

    useEffect(() => {
    if (!abierto) return;
    campos
        .filter((c) => c.optionsSource)
        .forEach(async (c) => {
        const datos = await adminApi.listar<any>(c.optionsSource!);
        if (datos) {
            setOpcionesDinamicas((prev) => ({ ...prev, [c.name]: datos }));
        }
        });
    }, [abierto, campos]);

    if (!abierto) return null;

    const handleChange = (nombre: string, valor: string | boolean) => {
    setValores((prev) => ({ ...prev, [nombre]: valor }));
    };

    const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onGuardar(valores);
    };

    return (
    <div
        className="modal"
        style={{ display: 'flex' }}
        onClick={(e) => {
        if (e.target === e.currentTarget) onCerrar();
        }}
    >
        <div className="modal-content">
        <span className="close-btn" onClick={onCerrar}>&times;</span>
        <h2>{titulo}</h2>
        <form onSubmit={handleSubmit}>
            {campos.map((campo) => (
            <div className="form-group" key={campo.name}>
                <label htmlFor={campo.name}>{campo.label}</label>

                {campo.type === 'select' && (
                <select
                    id={campo.name}
                    value={String(valores[campo.name] ?? '')}
                    onChange={(e) => handleChange(campo.name, e.target.value)}
                    required={campo.required !== false}
                >
                    <option value="" disabled>Selecciona una opción</option>
                    {campo.optionsSource
                    ? (opcionesDinamicas[campo.name] ?? []).map((opcion) => (
                        <option
                            key={opcion[campo.optionValueKey ?? 'id']}
                            value={opcion[campo.optionValueKey ?? 'id']}
                        >
                            {opcion[campo.optionLabelKey ?? 'nombre']}
                        </option>
                        ))
                    : campo.options?.map((opcion) => (
                        <option key={opcion} value={opcion}>
                            {opcion}
                        </option>
                        ))}
                </select>
                )}

                {campo.type === 'checkbox' && (
                <input
                    id={campo.name}
                    type="checkbox"
                    checked={Boolean(valores[campo.name])}
                    onChange={(e) => handleChange(campo.name, e.target.checked)}
                />
                )}

                {campo.type === 'textarea' && (
                <textarea
                    id={campo.name}
                    value={String(valores[campo.name] ?? '')}
                    onChange={(e) => handleChange(campo.name, e.target.value)}
                    required={campo.required !== false}
                />
                )}

                {['text', 'email', 'number', 'date', 'datetime-local'].includes(campo.type) && (
                <input
                    id={campo.name}
                    type={campo.type}
                    step={campo.type === 'number' ? 'any' : undefined}
                    min={campo.min}
                    max={campo.max}
                    value={String(valores[campo.name] ?? '')}
                    onChange={(e) => handleChange(campo.name, e.target.value)}
                    required={campo.required !== false}
                />
                )}
            </div>
            ))}

            <button type="submit" className="btn btn-primary" disabled={guardando}>
            {guardando ? 'Guardando...' : 'Guardar Cambios'}
            </button>
        </form>
        </div>
    </div>
    );
};

export default FormularioModal;