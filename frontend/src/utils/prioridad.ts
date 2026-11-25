export type PrioridadChip="baja"|"media"|"alta"

export const ETIQUETAS_PRIORIDAD:Record<PrioridadChip, string>={
    baja:"Prioridad baja",
    media:"Prioridad media",
    alta:"Prioridad alta"
};

// En el backend 5 es la maxima urgencia y 1 menos urgente
export function mapearPrioridad(Prioridad:number|null|undefined): PrioridadChip|null{
    if (Prioridad==null) return null;
    if (Prioridad>= 4)return "alta";
    if (Prioridad===3)return"media";
    return "baja"
}