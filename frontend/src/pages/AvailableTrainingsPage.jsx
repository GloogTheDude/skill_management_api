import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAvailableTrainings } from "../api/trainings";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

function formatDate(value) {
  if (!value) return "Date non renseignée";
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

export default function AvailableTrainingsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [trainings, setTrainings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadTrainings() {
      setLoading(true);
      setError(null);
      try {
        const availableTrainings = await getAvailableTrainings(user.id_employee);
        if (!cancelled) setTrainings(availableTrainings);
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

    loadTrainings();
    return () => { cancelled = true; };
  }, [user.id_employee, logout, navigate]);

  if (loading) return <div className="screen-state">Chargement des formations disponibles…</div>;

  if (error) {
    const message = error instanceof ApiError && error.status === 403
      ? "Vous n’êtes pas autorisé à consulter ces formations."
      : "Impossible de charger les formations disponibles. Réessayez plus tard.";
    return <div className="alert page-alert" role="alert">{message}</div>;
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Catalogue personnalisé</p>
          <h1>Formations disponibles</h1>
        </div>
        <span className="skill-count">{trainings.length} formation{trainings.length === 1 ? "" : "s"}</span>
      </div>

      {trainings.length === 0 ? (
        <div className="empty-state">
          <h2>Aucune formation disponible</h2>
          <p>Il n’y a actuellement aucune formation correspondant à votre situation.</p>
        </div>
      ) : (
        <div className="training-grid">
          {trainings.map((training) => (
            <article className="training-card" key={training.id_training}>
              <p className="eyebrow">{training.domaine_name}</p>
              <h2>{training.title || "Formation sans titre"}</h2>
              <dl className="training-dates">
                <div><dt>Du</dt><dd>{formatDate(training.start_)}</dd></div>
                <div><dt>Au</dt><dd>{formatDate(training.end_)}</dd></div>
              </dl>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
