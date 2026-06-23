import { apiClient } from "@/services/apiClient";
import type { TokenResponse, UserMe } from "@/services/types";

export const authService = {
  async register(email: string, username: string, password: string, role: "tester" | "developer") {
    const resp = await apiClient.post<UserMe>("/auth/register", { email, username, password, role });
    return resp.data;
  },

  async login(email: string, password: string) {
    const resp = await apiClient.post<TokenResponse>("/auth/login", { email, password });
    return resp.data;
  },

  async logout(refreshToken: string) {
    await apiClient.post("/auth/logout", { refresh_token: refreshToken });
  },

  async me() {
    const resp = await apiClient.get<UserMe>("/users/me");
    return resp.data;
  },
};
