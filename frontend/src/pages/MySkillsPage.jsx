import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getEmployeeSkillProfile } from "../api/skills";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

function formatDate(value) {
  if (!value) return null;
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function SourceList({ sources }) {
  return (
    <ul className="skill-sources">
      {sources.map((source) => (
        <li key={`${source.source_type}-${source.source_id}`}>
          <span>{source.source_type}</span>
          {source.level !== null && <span>Niveau {source.level}</span>}
          {!source.is_active && <span className="source-inactive">Inactive</span>}
          {source.expires_at && <span>Expire le {formatDate(source.expires_at)}</span>}
        </li>
      ))}
    </ul>
  );
}

export default function MySkillsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      setLoading(true);
      setError(null);
      try {
        const profile = await getEmployeeSkillProfile(user.id_employee);
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
  }, [user.id_employee, logout, navigate]);

  if (loading) return <div className="screen-state">Chargement de vos compétences…</div>;

  if (error) {
    const message = error instanceof ApiError && error.status === 403
      ? "Vous n’êtes pas autorisé à consulter ce profil."
      : "Impossible de charger votre profil de compétences. Réessayez plus tard.";
    return <div className="alert page-alert" role="alert">{message}</div>;
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Profil de compétences</p>
          <h1>Mes compétences</h1>
        </div>
        <span className="skill-count">{skills.length} compétence{skills.length === 1 ? "" : "s"}</span>
      </div>

      {skills.length === 0 ? (
        <div className="empty-state">
          <h2>Aucune compétence à afficher</h2>
          <p>Votre profil ne contient pas encore de compétence acquise ou validée.</p>
        </div>
      ) : (
        <div className="skills-grid">
          {skills.map((skill) => (
            <article className="skill-card" key={skill.skill_id}>
              <div className="skill-card-header">
                <div>
                  <h2>{skill.skill_name}</h2>
                  <p>{skill.skill_domaine || "Domaine non renseigné"}</p>
                </div>
                {skill.displayed_level !== null && (
                  <span className="level-badge">Niveau {skill.displayed_level}</span>
                )}
              </div>
              {skill.primary_source && (
                <p className="primary-source">Source principale : {skill.primary_source.source_type}</p>
              )}
              {skill.sources?.length > 0 && (
                <details>
                  <summary>{skill.sources.length} source{skill.sources.length === 1 ? "" : "s"}</summary>
                  <SourceList sources={skill.sources} />
                </details>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
