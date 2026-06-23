import { create } from "zustand";
import type { UserMe } from "@/services/types";

const ACCESS_TOKEN_KEY = "bha_access_token";
const REFRESH_TOKEN_KEY = "bha_refresh_token";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserMe | null;
  isInitializing: boolean;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: UserMe | null) => void;
  clear: () => void;
  finishInitializing: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(ACCESS_TOKEN_KEY),
  refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
  user: null,
  isInitializing: true,
  setTokens: (access, refresh) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  setUser: (user) => set({ user }),
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    set({ accessToken: null, refreshToken: null, user: null });
  },
  finishInitializing: () => set({ isInitializing: false }),
}));
