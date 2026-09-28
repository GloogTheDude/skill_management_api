import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { getEmployeeSkillProfile } from "../api/skills";
import SkillProfileList from "../components/SkillProfileList";
import { useAuth } from "../auth/AuthContext";

export default function EmployeeSkillProfilePage() {
  const { idEmployee } = useParams();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function loadProfile() {
      setLoading(true);
      setError(null);
      try {
        const profile = await getEmployeeSkillProfile(idEmployee);
        if (!cancelled) setSkills(profile);
      } catch (requestError) {
        if (cancelled) return;
        if (requestError instanceof ApiError && requestError.status === 401) {
          await logout().catch(() => undefined);
          navigate("/login", { replace: true });
          return;
        }
        setError(requestError);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadProfile();
    return () => { cancelled = true; };
  }, [idEmployee, logout, navigate]);

  if (loading) return <div className="screen-state">Chargement du profil de compétences…</div>;
  if (error) {
    let message = "Impossible de charger ce profil de compétences. Réessayez plus tard.";
    if (error instanceof ApiError && error.status === 403) message = "Vous n’êtes pas autorisé à consulter ce profil.";
    if (error instanceof ApiError && error.status === 404) message = "Cet Employee ou ce profil n’existe pas.";
    return (
      <div>
        <div className="alert page-alert" role="alert">{message}</div>
        {location.state?.returnTo && <button className="button button-secondary" type="button" onClick={() => navigate(location.state.returnTo)}>Retour aux résultats</button>}
      </div>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">Profil de compétences</p><h1>Profil de compétences</h1></div>
        <span className="skill-count">{skills.length} compétence{skills.length === 1 ? "" : "s"}</span>
      </div>
      {location.state?.returnTo && <button className="button button-secondary profile-back-button" type="button" onClick={() => navigate(location.state.returnTo)}>Retour aux résultats</button>}
      {skills.length === 0 ? (
        <div className="empty-state"><h2>Aucune compétence à afficher</h2><p>Ce profil ne contient pas encore de compétence acquise ou validée.</p></div>
      ) : <SkillProfileList skills={skills} />}
    </section>
  );
}
