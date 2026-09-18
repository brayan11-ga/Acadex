// src/components/estadisticas/EstadisticasAdmin.tsx
import React from 'react';

export interface ItemResumen {
  label: string;
  valor: number;
}

interface Props {
  titulo: string;
  items: ItemResumen[];
  cargando: boolean;
}

export const EstadisticasAdmin: React.FC<Props> = ({ titulo, items, cargando }) => {
  if (cargando) {
    return (
      <div className="p-6 text-white text-center">
        <p>Cargando resumen de administración...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-white mb-6">{titulo}</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((item, index) => (
          <div key={index} className="bg-[#12141c] border border-[#1f2430] p-4 rounded-xl shadow-md">
            <span className="text-gray-400 text-xs uppercase">{item.label}</span>
            <p className="text-2xl font-bold text-white mt-1">{item.valor}</p>
          </div>
        ))}
      </div>
    </div>
  );
};