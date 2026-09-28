import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute() {
  const { authenticated, loading } = useAuth();
  if (loading) return <div className="screen-state">Restauration de la session…</div>;
  return authenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
