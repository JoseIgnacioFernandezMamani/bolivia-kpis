import { GeoJsonLayer } from '@deck.gl/layers';
import type { FeatureCollection } from 'geojson';

type HoverHandler = (info: { object: unknown; x: number; y: number }) => void;

/** Choropleth layer for election results by department. */
export function getPoliticsLayer(data: FeatureCollection, onHover: HoverHandler) {
  return new GeoJsonLayer({
    id: 'politics-layer',
    data,
    pickable: true,
    stroked: true,
    filled: true,
    lineWidthMinPixels: 1,
    getFillColor: (f) => {
      // Simple party-colour mapping (extend as needed)
      const party: string = (f.properties?.party ?? '').toLowerCase();
      if (party.includes('mas')) return [0, 122, 61, 180];      // MAS – green
      if (party.includes('cc')) return [13, 110, 253, 180];     // CC – blue
      if (party.includes('creemos')) return [255, 193, 7, 180]; // Creemos – yellow
      return [150, 150, 150, 160];
    },
    getLineColor: [255, 255, 255, 120],
    onHover,
  });
}
