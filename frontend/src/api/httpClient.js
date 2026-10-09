import { tokenStorage } from "../auth/tokenStorage.js";

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => (onUnauthorized = fn);

export async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = tokenStorage.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth) onUnauthorized(); // sesión inválida: cerrar de inmediato
  if (!res.ok) {
    let detail = "Error en la solicitud";
    try { detail = (await res.json()).detail ?? detail; } catch { /* sin cuerpo */ }
    const err = new Error(typeof detail === "string" ? detail : "Datos inválidos");
    err.status = res.status;
    throw err;
  }
  return res.json();
}
