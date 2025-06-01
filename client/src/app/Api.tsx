import apiClient from "@/utils/apiClient";
import { services, servicesWait } from "@/utils/loadServices";

/*
API async functions below
*/

export async function postLogin(username, password) {
  await servicesWait();
  return apiClient
    .post(`${services.controller.url}/user/login`, {
      username: username,
      password: password
    })
    .then((response) => {
      return response.data.access_token;
    })
    .catch((error) => {
      throw error;
    });
}

export async function postSignup(username: string, email: string, password: string, phone?: string) {
  await servicesWait();
  return apiClient
    .post(`${services.controller.url}/user/signup`, {
      username,
      email,
      password,
      phone
    })
    .then((response) => {
      return response.data.message;
    })
    .catch((error) => {
      throw error;
    });
}

export async function fetchUserSelfData(token) {
  await servicesWait();
  return apiClient
    .get(`${services.controller.url}/user/self`, {
      headers: {
        Authorization: `Bearer ${token}`,
      }
    })
    .then((response) => response.data)
    .catch((error) => {
      throw error;
    });
}

export async function fetchLoodspots() {
  await servicesWait();

  return apiClient
    .get(`${services.controller.url}/route/loodspots`)
    .then((response) => response.data.loodspots)
    .catch((error) => []);
}

export async function fetchRoutes(token) {
  await servicesWait();

  return apiClient
    .get(`${services.controller.url}/route/`, { 
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((response) => response.data)
    .catch((error) => {
      throw error;
    });
}

export async function deleteRoute(token, routeId) {
  await servicesWait();

  return apiClient
    .delete(`${services.controller.url}/route/`, {
      data: {
        id: routeId, 
      },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((response) => true)
    .catch((error) => false);
}
export async function generateRoute(
  token,
  latitude,
  longitude,
  declared_distance,
  is_prefer_green,
  is_avoid_green,
  is_include_weather
) {
  await servicesWait();

  return apiClient
    .post(`${services.controller.url}/route/`, 
      {
        point: {latitude, longitude},
        declared_distance,
        is_prefer_green,
        is_avoid_green,
        is_include_weather
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      }
    )
    .then((response) => response.data)
    .catch((err) => {
      if (err.response && err.response.status === 429) {
        return { error: 'rate_limit_exceeded' };
      }
      return false;
    });
}
