'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { DeckGL } from '@deck.gl/react';
import { MapView } from '@deck.gl/core';
import { GeoJsonLayer } from '@deck.gl/layers';
import { Protocol } from 'pmtiles';
import 'maplibre-gl/dist/maplibre-gl.css';

import { getEconomyLayer } from './layers/EconomyLayer';
import { getPoliticsLayer } from './layers/PoliticsLayer';
import { getEnvironmentLayer } from './layers/EnvironmentLayer';
import MapTooltip, { TooltipInfo } from './MapTooltip';
import { fetchGeoJSON } from '@/lib/api';

export interface ActiveLayers {
  economy: boolean;
  politics: boolean;
  environment: boolean;
  security: boolean;
  society: boolean;
  technology: boolean;
}

interface Props {
  activeLayers: ActiveLayers;
}

const INITIAL_VIEW_STATE = {
  longitude: -64.9,
  latitude: -16.5,
  zoom: 5.5,
  pitch: 0,
  bearing: 0,
};

const MAP_STYLE =
  process.env.NEXT_PUBLIC_MAPLIBRE_STYLE ||
  'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

export default function MapContainer({ activeLayers }: Props) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  // GeoJSON data caches
  const [economyData, setEconomyData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [politicsData, setPoliticsData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [environmentData, setEnvironmentData] = useState<GeoJSON.FeatureCollection | null>(null);

  // Register PMTiles protocol once
  useEffect(() => {
    const protocol = new Protocol();
    maplibregl.addProtocol('pmtiles', protocol.tile);
    return () => {
      maplibregl.removeProtocol('pmtiles');
    };
  }, []);

  // Initialise MapLibre map
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: MAP_STYLE,
      center: [INITIAL_VIEW_STATE.longitude, INITIAL_VIEW_STATE.latitude],
      zoom: INITIAL_VIEW_STATE.zoom,
      attributionControl: true,
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Lazy-load GeoJSON when layer is toggled on
  useEffect(() => {
    if (activeLayers.economy && !economyData) {
      fetchGeoJSON('/economy/contracts/geojson').then(setEconomyData).catch((err) => {
        console.error('Failed to load economy layer:', err);
      });
    }
  }, [activeLayers.economy, economyData]);

  useEffect(() => {
    if (activeLayers.politics && !politicsData) {
      fetchGeoJSON('/politics/elections/geojson').then(setPoliticsData).catch((err) => {
        console.error('Failed to load politics layer:', err);
      });
    }
  }, [activeLayers.politics, politicsData]);

  useEffect(() => {
    if (activeLayers.environment && !environmentData) {
      fetchGeoJSON('/environment/deforestation').then(setEnvironmentData).catch((err) => {
        console.error('Failed to load environment layer:', err);
      });
    }
  }, [activeLayers.environment, environmentData]);

  const handleHover = useCallback(({ object, x, y }: { object: unknown; x: number; y: number }) => {
    if (object) {
      setTooltip({ object: object as Record<string, unknown>, x, y });
    } else {
      setTooltip(null);
    }
  }, []);

  // Build Deck.gl layers
  const deckLayers = [
    ...(activeLayers.economy && economyData
      ? [getEconomyLayer(economyData, handleHover)]
      : []),
    ...(activeLayers.politics && politicsData
      ? [getPoliticsLayer(politicsData, handleHover)]
      : []),
    ...(activeLayers.environment && environmentData
      ? [getEnvironmentLayer(environmentData, handleHover)]
      : []),
  ];

  return (
    <div className="relative h-full w-full">
      {/* MapLibre base map */}
      <div ref={mapContainer} className="absolute inset-0" />

      {/* Deck.gl overlay */}
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: vs }) => setViewState(vs as typeof INITIAL_VIEW_STATE)}
        controller
        layers={deckLayers}
        style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
        views={new MapView({ repeat: true })}
      />

      {/* Tooltip */}
      {tooltip && <MapTooltip info={tooltip} />}
    </div>
  );
}
