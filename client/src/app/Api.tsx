// client / src / app / Api.tsx
//---------------------------------------------------------------
// 1. Importy + bazowy adres backendu
//---------------------------------------------------------------
import apiClient from "@/utils/apiClient";
import { services, servicesWait } from "@/utils/loadServices";

// jeżeli config‑serwer zwrócił wpis „controller”, użyjemy go;
// w przeciwnym razie łączymy się lokalnie na 5001
const getBaseUrl = () => services.controller?.url || "http://localhost:5001";

//---------------------------------------------------------------
// 2. Typy
//---------------------------------------------------------------
interface TokenResponse  { access_token: string }
interface SignupResponse { message: string  }
interface PostsResponse  { posts: any[]     }

export interface RouteGeoJSON {
  type: "LineString";
  coordinates: number[][];
}

export interface BackendRoute {
  id: number;
  decl_distance: number;
  is_avoid_green: boolean;
  is_prefer_green: boolean;
  is_include_weather: boolean;
  route: string;                 // GeoJSON zakodowany jako string
  timestamp: string;
}

export interface SavedRoute extends Omit<BackendRoute, "route"> {
  geojson: RouteGeoJSON;
}

//---------------------------------------------------------------
// 3. Autoryzacja
//---------------------------------------------------------------
export async function postLogin(
  username: string,
  password: string
): Promise<string> {
  await servicesWait();

  const { data } = await apiClient.post<TokenResponse>(
    `${getBaseUrl()}/user/login`,
    { username, password }
  );
  return data.access_token;
}

export async function postSignup(
  username: string,
  email: string,
  password: string,
  phone?: string
): Promise<string> {
  await servicesWait();

  const { data } = await apiClient.post<SignupResponse>(
    `${getBaseUrl()}/user/signup`,
    { username, email, password, phone }
  );
  return data.message;
}

export async function fetchUserSelfData(token: string) {
  await servicesWait();

  const { data } = await apiClient.get(`${getBaseUrl()}/user/self`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
}

//---------------------------------------------------------------
// 4. Posty (jeżeli korzystasz z feedu)
//---------------------------------------------------------------
export async function fetchPosts(
  user_id: string | null = null,
  last_timestamp: string | null = null,
  limit = 10
) {
  await servicesWait();

  const params = {
    limit,
    ...(user_id && { user_id }),
    ...(last_timestamp && { last_timestamp }),
  };

  const { data } = await apiClient.get<PostsResponse>(
    `${getBaseUrl()}/post`,
    { params }
  );
  return data.posts;
}

export async function getPost(token: string, postId: string) {
  await servicesWait();

  const { data } = await apiClient.get(`${getBaseUrl()}/post/single`, {
    params: { id: postId },
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
}

//---------------------------------------------------------------
// 5. Trasy: generuj / pobierz / zapisz / usuń
//---------------------------------------------------------------
export async function generateRoute(
  token: string,
  latitude: number,
  longitude: number,
  declared_distance: number,
  is_prefer_green: boolean,
  is_avoid_green: boolean,
  is_include_weather: boolean
): Promise<BackendRoute> {
  await servicesWait();

  const { data } = await apiClient.post<BackendRoute>(
    `${getBaseUrl()}/route/`,
    {
      point: { latitude, longitude },
      declared_distance,
      is_prefer_green,
      is_avoid_green,
      is_include_weather,
    },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return data;
}

export async function getRoutes(token: string): Promise<SavedRoute[]> {
  await servicesWait();

  const { data } = await apiClient.get<{ routes: BackendRoute[] }>(
    `${getBaseUrl()}/route/`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  return data.routes.map((r) => ({
    ...r,
    geojson: JSON.parse(r.route),
  }));
}

export async function saveRoute(
  token: string,
  payload: BackendRoute
): Promise<SavedRoute> {
  await servicesWait();

  const { data } = await apiClient.post<BackendRoute>(
    `${getBaseUrl()}/route/`,
    payload,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  return { ...data, geojson: JSON.parse(data.route) };
}

export async function removeRoute(
  token: string,
  routeId: number
): Promise<void> {
  await servicesWait();

  await apiClient.delete(`${getBaseUrl()}/route/${routeId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}




