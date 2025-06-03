"use client";

import axios from 'axios';
import Cookies from 'js-cookie';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response &&
      error.response.status === 401 &&
      error.config &&
      !error.config.url.includes("/user/login")
    ) {
      Cookies.remove("token");
      window.location.href = "/about";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
