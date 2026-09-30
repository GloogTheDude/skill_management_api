import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

function navigationFor(permissionProfile) {
  const employee = [
    ["/app", "Accueil"],
    ["/app/skills", "Mes compétences"],
    ["/app/trainings", "Formations disponibles"],
    ["/app/training-requests", "Mes demandes"],
    ["/app/participations", "Participations"],
  ];
  if (permissionProfile === "EMPLOYEE") return employee;
  if (permissionProfile === "MANAGER") {
    return [...employee, ["/app/manage-requests", "Demandes à traiter"], ["/app/employee-search", "Recherche employés"]];
  }
  return [
    ...employee,
    ["/app/employee-search", "Recherche employés"],
    ["/app/manage-requests", "Demandes à traiter"],
    ["/app/employees", "Employees"],
    ["/app/training-admin", "Trainings"],
    ["/app/references", "Référentiels"],
  ];
}

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const links = navigationFor(user.permission_profile);

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Skill Management</div>
        <nav aria-label="Navigation principale">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/app"} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div>
            <strong>{user.first_name} {user.last_name}</strong>
            <span>{user.role_name || user.access_level_label || "Utilisateur"}</span>
          </div>
          <button className="button button-secondary" onClick={handleLogout}>Se déconnecter</button>
        </header>
        <div className="page-content"><Outlet /></div>
      </main>
    </div>
  );
}
