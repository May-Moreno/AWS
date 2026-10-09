import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";
import Button from "../components/Button.jsx";
import Card from "../components/Card.jsx";
import TextField from "../components/TextField.jsx";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(username.trim(), password);
      navigate(location.state?.from?.pathname ?? "/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="center">
      <Card title="Iniciar sesión">
        <form onSubmit={onSubmit} className="form">
          <TextField id="user" label="Usuario" value={username} autoComplete="username"
            onChange={(e) => setUsername(e.target.value)} required minLength={3} maxLength={50} />
          <TextField id="pass" label="Contraseña" type="password" value={password}
            autoComplete="current-password" onChange={(e) => setPassword(e.target.value)}
            required minLength={8} maxLength={128} />
          {error && <p className="error" role="alert">{error}</p>}
          <Button type="submit" disabled={busy}>{busy ? "Verificando…" : "Entrar"}</Button>
        </form>
      </Card>
    </div>
  );
}
