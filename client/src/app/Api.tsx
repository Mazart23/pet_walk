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

export async function fetchPosts(user_id = null, last_timestamp = null, limit = 10) {
  await servicesWait();

  const params = {
    limit,
    ...(user_id && { user_id }),
    ...(last_timestamp && { last_timestamp }),
  };

  try {
    const response = await apiClient.get(`${services.controller.url}/post`, { params });
    return response.data.posts;
  } catch (error) {
    console.error("Error fetching posts:", error.response?.data || error.message);
    throw error;
  }
}

export async function getPost(token, postId) {
  await servicesWait();

  return apiClient
    .get(`${services.controller.url}/post/single`, { 
      params: { 
        id: postId 
      },
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((response) => response.data)
    .catch((error) => {
      throw error;
    });
}

export async function createPost(token, formData: FormData) {
  await servicesWait();

  return apiClient
    .put(`${services.controller.url}/post/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => response.data)
    .catch((error) => {
      console.error("Error creating post:", error.response?.data || error.message);
      throw error;
    });
}
