import { List, LayoutGrid } from "lucide-react";
import "../../styles/toggle-vista.css";

export type ModoVista = "lista" | "cuadricula";

interface ToggleVistaProps {
    valor: ModoVista;
    onCambiar: (modo: ModoVista) => void;
}

export const ToggleVista = ({ valor, onCambiar }: ToggleVistaProps) => (
    <div className="toggle-vista" role="group" aria-label="Tipo de vista">
    <button type="button" aria-pressed={valor === "lista"} onClick={() => onCambiar("lista")}>
        <List size={16} /> Lista
    </button>
    <button type="button" aria-pressed={valor === "cuadricula"} onClick={() => onCambiar("cuadricula")}>
        <LayoutGrid size={16} /> Cuadrícula
    </button>
    </div>
);