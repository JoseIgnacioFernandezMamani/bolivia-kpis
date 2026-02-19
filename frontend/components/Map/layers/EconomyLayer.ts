import { GeoJsonLayer } from '@deck.gl/layers';
import type { FeatureCollection } from 'geojson';

type HoverHandler = (info: { object: unknown; x: number; y: number }) => void;

/** Choropleth layer for public contracts / GDP data. */
export function getEconomyLayer(data: FeatureCollection, onHover: HoverHandler) {
  return new GeoJsonLayer({
    id: 'economy-layer',
    data,
    pickable: true,
    stroked: true,
    filled: true,
    pointRadiusMinPixels: 5,
    lineWidthMinPixels: 1,
    getFillColor: (f) => {
      const amount = (f.properties?.amount as number) ?? 0;
      const intensity = Math.min(255, Math.floor((amount / 1_000_000) * 50));
      return [255 - intensity, 200, intensity, 160];
    },
    getLineColor: [255, 255, 255, 120],
    onHover,
  });
}
