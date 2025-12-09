// shared/api/auth.ts
import { api, setAuthToken, clearAuthToken } from "./api";

export interface User {
  _id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  message?: string;
}

export async function signup(email: string, password: string, name: string): Promise<AuthResponse> {
  const response = await api.post("/api/auth/signup", { email, password, name });
  setAuthToken(response.data.token);
  localStorage.setItem("user", JSON.stringify(response.data.user));
  return response.data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await api.post("/api/auth/login", { email, password });
  setAuthToken(response.data.token);
  localStorage.setItem("user", JSON.stringify(response.data.user));
  return response.data;
}

export async function logout(): Promise<void> {
  clearAuthToken();
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get("/api/auth/me");
  return response.data;
}

export function getStoredUser(): User | null {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
}

export function getStoredToken(): string | null {
  return localStorage.getItem("token");
}

