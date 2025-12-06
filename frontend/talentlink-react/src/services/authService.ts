import axios from 'axios';

const BASE_URL = 'http://talentlink.local/api/auth';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: string;
}

export class AuthService {
  static async login(username: string, password: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<LoginResponse>(`${BASE_URL}/login`, {
        username,
        password,
      });
      return response.data;
    } catch (error: any) {
      const message = 
        error.response?.data?.error || 
        error.message || 
        'Login failed - please check your credentials';
      console.error('AuthService login error:', error);
      throw new Error(message);
    }
  }

  static async register(data: RegisterRequest): Promise<void> {
    try {
      await axios.post(`${BASE_URL}/register`, data);
    } catch (error: any) {
      const message = 
        error.response?.data?.error || 
        error.message || 
        'Registration failed - please try again';
      console.error('AuthService register error:', error);
      throw new Error(message);
    }
  }

  static async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${BASE_URL}/health`);
      return response.status === 200;
    } catch {
      return false;
    }
  }
}
