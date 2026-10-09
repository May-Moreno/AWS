import { useAuth } from "../auth/AuthContext.jsx";
import Button from "./Button.jsx";

export default function AppLayout({ children }) {
  const { user, logout } = useAuth();
  return (
    <div>
      <header className="topbar">
        <strong>Panel Zero Trust</strong>
        <div className="topbar-right">
          <span>{user.username} · {user.role}</span>
          <Button variant="ghost" onClick={logout}>Cerrar sesión</Button>
        </div>
      </header>
      <main className="container">{children}</main>
    </div>
  );
}
