// sessionStorage: el token desaparece al cerrar la pestaña (menor exposición que localStorage).
const KEY = "zt_token";

export const tokenStorage = {
  get: () => sessionStorage.getItem(KEY),
  set: (t) => sessionStorage.setItem(KEY, t),
  clear: () => sessionStorage.removeItem(KEY),
};

export function decodeToken(token) {
  try {
    const payload = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

export function isExpired(token) {
  const data = decodeToken(token);
  return !data || data.exp * 1000 <= Date.now();
}
