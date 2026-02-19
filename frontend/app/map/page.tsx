'use client';

import dynamic from 'next/dynamic';
import LayerControl from '@/components/Map/LayerControl';
import { useState } from 'react';
import type { ActiveLayers } from '@/components/Map/MapContainer';

// Dynamically import the map to avoid SSR issues with MapLibre
const MapContainer = dynamic(() => import('@/components/Map/MapContainer'), {
  ssr: false,
  loading: () => (
    <div className="flex h-screen w-full items-center justify-center bg-gray-900 text-white">
      <p className="text-lg animate-pulse">Cargando mapa…</p>
    </div>
  ),
});

const DEFAULT_LAYERS: ActiveLayers = {
  economy: false,
  politics: false,
  environment: false,
  security: false,
  society: false,
  technology: false,
};

export default function MapPage() {
  const [activeLayers, setActiveLayers] = useState<ActiveLayers>(DEFAULT_LAYERS);

  const toggleLayer = (layer: keyof ActiveLayers) => {
    setActiveLayers((prev) => ({ ...prev, [layer]: !prev[layer] }));
  };

  return (
    <main className="relative h-screen w-full overflow-hidden">
      {/* Map fills the viewport */}
      <MapContainer activeLayers={activeLayers} />

      {/* Sidebar / layer control */}
      <aside className="absolute top-4 left-4 z-10 w-60 rounded-xl bg-white/90 shadow-xl backdrop-blur-sm">
        <div className="border-b px-4 py-3">
          <h1 className="text-lg font-bold text-gray-800">Bolivia KPIs</h1>
          <p className="text-xs text-gray-500">Capas de datos</p>
        </div>
        <LayerControl activeLayers={activeLayers} onToggle={toggleLayer} />
      </aside>
    </main>
  );
}
