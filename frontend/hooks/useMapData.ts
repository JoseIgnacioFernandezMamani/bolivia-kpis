import useSWR from 'swr';
import { fetchGeoJSON } from '@/lib/api';
import type { FeatureCollection } from 'geojson';

/**
 * Fetches a GeoJSON FeatureCollection from the API and caches it via SWR.
 * Data is only fetched when `enabled` is true (lazy loading).
 */
export function useMapData(endpoint: string, enabled: boolean = true) {
  const { data, error, isLoading } = useSWR<FeatureCollection>(
    enabled ? endpoint : null,
    fetchGeoJSON,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 5 * 60 * 1000, // 5 minutes
    },
  );

  return {
    data: data ?? null,
    isLoading,
    isError: !!error,
  };
}
