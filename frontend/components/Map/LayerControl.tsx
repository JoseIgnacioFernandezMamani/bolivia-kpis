'use client';

import type { ActiveLayers } from './MapContainer';

interface LayerMeta {
  key: keyof ActiveLayers;
  label: string;
  color: string;
  description: string;
}

const LAYERS: LayerMeta[] = [
  { key: 'economy', label: 'Economía', color: 'bg-emerald-500', description: 'Contratos, PIB, exportaciones' },
  { key: 'politics', label: 'Política', description: 'Elecciones, conflictos, TIOC', color: 'bg-blue-600' },
  { key: 'environment', label: 'Medio Ambiente', color: 'bg-yellow-500', description: 'Deforestación, incendios, minería' },
  { key: 'security', label: 'Seguridad', color: 'bg-red-600', description: 'Crimen, decomisos, infraestructura' },
  { key: 'society', label: 'Sociedad', color: 'bg-purple-600', description: 'IDH, censo, brecha de género' },
  { key: 'technology', label: 'Tecnología', color: 'bg-sky-500', description: 'Internet, cobertura, I+D' },
];

interface Props {
  activeLayers: ActiveLayers;
  onToggle: (layer: keyof ActiveLayers) => void;
}

export default function LayerControl({ activeLayers, onToggle }: Props) {
  return (
    <ul className="divide-y divide-gray-100">
      {LAYERS.map(({ key, label, color, description }) => (
        <li key={key} className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer" onClick={() => onToggle(key)}>
          <span className={`h-3 w-3 flex-shrink-0 rounded-full ${color}`} />
          <div className="flex-1 min-w-0">
            <p className="truncate text-sm font-medium text-gray-800">{label}</p>
            <p className="truncate text-xs text-gray-400">{description}</p>
          </div>
          <input
            type="checkbox"
            checked={activeLayers[key]}
            onChange={() => onToggle(key)}
            className="h-4 w-4 rounded accent-blue-600"
            aria-label={`Toggle ${label}`}
          />
        </li>
      ))}
    </ul>
  );
}
