import { useCallback, useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/authService";

export function useAuth() {
  const { accessToken, refreshToken, user, isInitializing, setTokens, setUser, clear, finishInitializing } =
    useAuthStore();

  useEffect(() => {
    let mounted = true;
    async function init() {
      if (accessToken) {
        try {
          const me = await authService.me();
          if (mounted) setUser(me);
        } catch {
          if (mounted) clear();
        }
      }
      if (mounted) finishInitializing();
    }
    init();
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await authService.login(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await authService.me();
      setUser(me);
      return me;
    },
    [setTokens, setUser]
  );

  const register = useCallback(
    async (email: string, username: string, password: string, role: "tester" | "developer") => {
      await authService.register(email, username, password, role);
      return login(email, password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    if (refreshToken) {
      try {
        await authService.logout(refreshToken);
      } catch {
        // ignore network errors on logout — clear client state regardless
      }
    }
    clear();
  }, [refreshToken, clear]);

  const refreshUser = useCallback(async () => {
    const me = await authService.me();
    setUser(me);
    return me;
  }, [setUser]);

  return {
    user,
    isAuthenticated: Boolean(accessToken && user),
    isInitializing,
    login,
    register,
    logout,
    refreshUser,
  };
}
