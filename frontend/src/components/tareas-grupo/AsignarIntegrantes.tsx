// Ruta: frontend/src/components/tareas-grupo/AsignarIntegrantes.tsx
import { useEffect, useId, useRef } from "react";
import type { IntegranteAsignable, RolIntegrante } from "../../types/tareaGrupo";
import "../../styles/tareas-grupo.css";

export type { IntegranteAsignable, RolIntegrante };

export interface AsignarIntegrantesProps {
  integrantes: IntegranteAsignable[];
  seleccionados: number[];
  onChange: (idsSeleccionados: number[]) => void;
  error?: string;
  usuarioActualId?: number | null;
  etiqueta?: string;
}

const ETIQUETAS_ROL: Record<RolIntegrante, string> = {
  lider: "Líder",
  miembro: "Miembro",
};

export const MENSAJE_SIN_ASIGNADOS = "Elige al menos un integrante";

export function validarAsignados(idsSeleccionados: number[]): string | undefined {
  return idsSeleccionados.length === 0 ? MENSAJE_SIN_ASIGNADOS : undefined;
}

function obtenerInicial(integrante: IntegranteAsignable): string {
  const base = integrante.nombre?.trim() || integrante.correo_electronico.trim();
  return base.charAt(0).toUpperCase() || "?";
}

function alternarId(ids: number[], id: number): number[] {
  return ids.includes(id) ? ids.filter((actual) => actual !== id) : [...ids, id];
}

function textoContador(cantidad: number): string {
  return cantidad === 1 ? "1 seleccionado" : `${cantidad} seleccionados`;
}

export default function AsignarIntegrantes({
  integrantes,
  seleccionados,
  onChange,
  error,
  usuarioActualId,
  etiqueta = "Asignar a",
}: AsignarIntegrantesProps) {
  const baseId = useId();
  const etiquetaId = `${baseId}-etiqueta`;
  const errorId = `${baseId}-error`;
  const casillaTodosRef = useRef<HTMLInputElement>(null);

  const idsValidos = seleccionados.filter((id) =>
    integrantes.some((integrante) => integrante.id_usuario === id),
  );
  const cantidad = idsValidos.length;
  const total = integrantes.length;
  const todosMarcados = total > 0 && cantidad === total;
  const algunosMarcados = cantidad > 0 && !todosMarcados;

  useEffect(() => {
    if (casillaTodosRef.current) casillaTodosRef.current.indeterminate = algunosMarcados;
  }, [algunosMarcados]);

  function alternarTodos() {
    onChange(todosMarcados ? [] : integrantes.map((integrante) => integrante.id_usuario));
  }

  return (
    <div
      role="group"
      aria-labelledby={etiquetaId}
      aria-describedby={error ? errorId : undefined}
      className={`tareas-grupo-asignar${error ? " tareas-grupo-asignar--error" : ""}`}
    >
      <div className="tareas-grupo-asignar-cabecera">
        <span id={etiquetaId} className="tareas-grupo-label">
          {etiqueta}
        </span>
        <span className="tareas-grupo-asignar-contador" aria-live="polite">
          {textoContador(cantidad)}
        </span>
      </div>

      {total === 0 ? (
        <p className="tareas-grupo-asignar-vacio">Este grupo aún no tiene integrantes.</p>
      ) : (
        <>
          <label className="tareas-grupo-asignar-todos">
            <input
              ref={casillaTodosRef}
              type="checkbox"
              className="tareas-grupo-check-input"
              checked={todosMarcados}
              onChange={alternarTodos}
            />
            <span className="tareas-grupo-check-caja" aria-hidden="true" />
            <span>Seleccionar todos</span>
          </label>

          <ul className="tareas-grupo-asignar-lista">
            {integrantes.map((integrante) => {
              const marcado = idsValidos.includes(integrante.id_usuario);
              const esUsuarioActual = integrante.id_usuario === usuarioActualId;
              return (
                <li key={integrante.id_usuario}>
                  <label
                    className={`tareas-grupo-asignar-fila${marcado ? " tareas-grupo-asignar-fila--seleccionada" : ""}`}
                  >
                    <input
                      type="checkbox"
                      className="tareas-grupo-check-input"
                      checked={marcado}
                      onChange={() => onChange(alternarId(idsValidos, integrante.id_usuario))}
                      aria-invalid={error ? true : undefined}
                    />
                    <span className="tareas-grupo-check-caja" aria-hidden="true" />
                    <span className="tareas-grupo-avatar" aria-hidden="true">
                      {obtenerInicial(integrante)}
                    </span>
                    <span className="tareas-grupo-asignar-info">
                      <span className="tareas-grupo-asignar-correo">
                        <span className="tareas-grupo-truncar">
                          {integrante.nombre || integrante.correo_electronico}
                        </span>
                        {esUsuarioActual && <span className="tareas-grupo-etiqueta-tu">TÚ</span>}
                      </span>
                      {integrante.nombre && (
                        <span className="tareas-grupo-asignar-secundario tareas-grupo-truncar">
                          {integrante.correo_electronico}
                        </span>
                      )}
                      <span className={`tareas-grupo-rol tareas-grupo-rol--${integrante.rol}`}>
                        {ETIQUETAS_ROL[integrante.rol]}
                      </span>
                    </span>
                  </label>
                </li>
              );
            })}
          </ul>
        </>
      )}

      {error && (
        <p id={errorId} role="alert" className="tareas-grupo-error-campo">
          <span aria-hidden="true">✕</span> {error}
        </p>
      )}
    </div>
  );
}
