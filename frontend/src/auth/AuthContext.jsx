import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../api/authApi.js";
import { setUnauthorizedHandler } from "../api/httpClient.js";
import { isExpired, tokenStorage } from "./tokenStorage.js";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  const login = useCallback(async (username, password) => {
    const { access_token } = await authApi.login(username, password);
    tokenStorage.set(access_token);
    setUser(await authApi.me()); // el backend es la fuente de verdad del rol y permisos
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(logout);
    const token = tokenStorage.get();
    if (!token || isExpired(token)) {
      logout();
      setLoading(false);
      return;
    }
    authApi.me().then(setUser).catch(logout).finally(() => setLoading(false));
  }, [logout]);

  // Revalidación periódica: cierra la sesión apenas expira el token.
  useEffect(() => {
    const id = setInterval(() => {
      const t = tokenStorage.get();
      if (t && isExpired(t)) logout();
    }, 15000);
    return () => clearInterval(id);
  }, [logout]);

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
