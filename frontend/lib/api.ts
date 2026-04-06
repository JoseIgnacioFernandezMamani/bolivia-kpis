const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Fetch a GeoJSON FeatureCollection from the backend API.
 * @param path - API path relative to the base URL, e.g. '/economy/contracts/geojson'
 */
export async function fetchGeoJSON(
    path: string,
): Promise<GeoJSON.FeatureCollection> {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`API error ${res.status}: ${res.statusText}`);
    }

    return res.json();
}

/**
 * Generic API fetch helper.
 */
export async function apiFetch<T = unknown>(path: string): Promise<T> {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url);

    if (!res.ok) {
        throw new Error(`API error ${res.status}: ${res.statusText}`);
    }

    return res.json();
}
