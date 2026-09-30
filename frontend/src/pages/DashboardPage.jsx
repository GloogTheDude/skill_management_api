import { useAuth } from "../auth/AuthContext";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { getDashboard } from "../api/dashboard";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    getDashboard().then(setData).catch((requestError) => {
      setError(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à consulter ce Dashboard."
        : "Le Dashboard est momentanément indisponible.");
    });
  }, []);
  if (!data && !error) return <div className="screen-state">Chargement du Dashboard…</div>;
  if (error) return <div className="alert page-alert" role="alert">{error}</div>;
  const cards = [
    ["Demandes à traiter", data.pending_training_requests, "/app/manage-requests?view=pending"],
    ["Évaluations à effectuer", data.pending_skill_evaluations, "/app/manage-evaluations?view=pending"],
    ["Participations actives", data.active_participations, "/app/participations?view=current"],
    ["Certifications dans les 30 jours", data.expiring_certifications, "/app/participations"],
  ];
  return (
    <section>
      <p className="eyebrow">Accueil</p>
      <h1>Bonjour {user.first_name || ""}.</h1>
      <div className="dashboard-grid">
        {cards.map(([label, value, target]) => (
          <button className="dashboard-card" type="button" key={label} onClick={() => navigate(target)}>
            <span>{label}</span><strong>{value}</strong>
          </button>
        ))}
      </div>
      {data.active_employees !== null && data.active_employees !== undefined && <p className="dashboard-note">Employees actifs dans votre périmètre : {data.active_employees}</p>}
      {data.acquired_skills !== null && data.acquired_skills !== undefined && <p className="dashboard-note">Vos compétences acquises : {data.acquired_skills} · évaluées : {data.evaluated_skills}</p>}
    </section>
  );
}
