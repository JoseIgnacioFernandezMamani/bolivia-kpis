import { GeoJsonLayer } from '@deck.gl/layers';
import type { FeatureCollection } from 'geojson';

type HoverHandler = (info: { object: unknown; x: number; y: number }) => void;

/** Layer visualising deforestation zones. */
export function getEnvironmentLayer(data: FeatureCollection, onHover: HoverHandler) {
  return new GeoJsonLayer({
    id: 'environment-layer',
    data,
    pickable: true,
    stroked: true,
    filled: true,
    lineWidthMinPixels: 1,
    getFillColor: (f) => {
      const areaHa = (f.properties?.area_ha as number) ?? 0;
      const intensity = Math.min(255, Math.floor((areaHa / 50_000) * 255));
      // Gradient from yellow to red as area increases
      return [255, 255 - intensity, 0, 160];
    },
    getLineColor: [180, 80, 0, 200],
    onHover,
  });
}
