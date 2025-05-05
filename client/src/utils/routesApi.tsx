// client/src/utils/routesApi.ts

import apiClient from "@/utils/apiClient";
import { services, servicesWait } from "@/utils/loadServices";

// Typ obiektu trasy z backendu (przed przetworzeniem GeoJSON)
export interface BackendRoute {
  id: number;
  decl_distance: number;
  is_avoid_green: boolean;
  is_prefer_green: boolean;
  is_include_weather: boolean;
  route: string; // zakodowany GeoJSON jako string
  timestamp: string;
}

// Typ obiektu po sparsowaniu route → geojson
export interface ParsedRoute extends Omit<BackendRoute, "route"> {
  geojson: any; // Możesz uściślić typ np. GeoJSON.LineString
}

const base = () => services.routes?.url || "http://localhost:8000";

// Pobieranie zapisanych tras
export const getRoutes = async (token: string): Promise<ParsedRoute[]> => {
  await servicesWait();
  const { data } = await apiClient.get<BackendRoute[]>(`${base()}/route/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data.map((r) => ({
    ...r,
    geojson: JSON.parse(r.route),
  }));
};

// Zapisywanie nowej trasy
export const saveRoute = async (
  token: string,
  payload: BackendRoute
): Promise<ParsedRoute> => {
  await servicesWait();
  const { data } = await apiClient.post<BackendRoute>(
    `${base()}/route/`,
    payload,
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return { ...data, geojson: JSON.parse(data.route) };
};

// Usuwanie trasy
export const removeRoute = async (
  token: string,
  id: number
): Promise<void> => {
  await servicesWait();
  await apiClient.delete(`${base()}/route/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
};
