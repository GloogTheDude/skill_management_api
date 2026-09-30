import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { getMyTeam } from "../api/employees";
import { useAuth } from "../auth/AuthContext";

export default function TeamPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [team, setTeam] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user?.permission_profile !== "MANAGER") {
      setLoading(false);
      return;
    }
    getMyTeam().then(setTeam).catch(async (requestError) => {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setError(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à consulter cette équipe."
        : "L’équipe n’a pas pu être chargée.");
    }).finally(() => setLoading(false));
  }, [logout, navigate, user]);

  if (user?.permission_profile !== "MANAGER") return <div className="alert page-alert">Cette page est réservée aux Managers.</div>;
  if (loading) return <div className="screen-state">Chargement de votre équipe…</div>;
  if (error) return <div className="alert page-alert" role="alert">{error}</div>;
  return <section>
    <div className="page-heading"><div><p className="eyebrow">Management</p><h1>Mon équipe</h1></div></div>
    {team.length === 0 ? <div className="empty-state"><h2>Aucun direct report</h2><p>Les Employees qui vous sont directement rattachés apparaîtront ici.</p></div> : <div className="reference-list">{team.map((employee) => <article className="reference-card" key={employee.id_employee}><div><p className="reference-primary">{employee.first_name} {employee.last_name}</p><p>{employee.mail || "Email non renseigné"}</p><p>{employee.denomination_role || "Rôle non renseigné"}</p></div><div className="card-actions"><button className="button button-secondary" type="button" onClick={() => navigate(`/app/employees/${employee.id_employee}/acquisitions`)}>Acquis</button><button className="button button-primary" type="button" onClick={() => navigate(`/app/manage-evaluations/${employee.id_employee}`)}>Évaluer</button></div></article>)}</div>}
  </section>;
}
