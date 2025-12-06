import axios from 'axios';
import { TokenStorage } from './tokenStorage';

export function setupAxiosInterceptors() {
  // Request interceptor to add auth token
  axios.interceptors.request.use(
    (config) => {
      const token = TokenStorage.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle 401
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        TokenStorage.clearTokens();
        // Redirect to login
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
}
