import { useEffect, useState } from "react";
import { dashboardApi } from "../api/authApi.js";
import AppLayout from "../components/AppLayout.jsx";
import Card from "../components/Card.jsx";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboardApi.summary().then(setSummary).catch((e) => setError(e.message));
    // Solo el rol admin tiene permiso; para otros el backend responde 403 y no se muestra nada.
    dashboardApi.users().then(setUsers).catch(() => setUsers(null));
  }, []);

  return (
    <AppLayout>
      <h2>Dashboard</h2>
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {summary?.metrics.map((m) => (
          <Card key={m.label} title={m.label}><p className="metric">{m.value}</p></Card>
        ))}
      </div>
      {users && (
        <Card title="Usuarios (solo administrador)">
          <table>
            <thead><tr><th>Usuario</th><th>Rol</th><th>Activo</th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.username}><td>{u.username}</td><td>{u.role}</td><td>{u.active ? "Sí" : "No"}</td></tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </AppLayout>
  );
}
