import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAvailableTrainings } from "../api/trainings";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { createPlannedTrainingRequest } from "../api/trainingRequests";

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
  const [submittingId, setSubmittingId] = useState(null);
  const [feedback, setFeedback] = useState("");

  const loadTrainings = useCallback(async () => {
      setLoading(true);
      setError(null);
      try {
        const availableTrainings = await getAvailableTrainings(user.id_employee);
        setTrainings(availableTrainings);
      } catch (requestError) {
        if (requestError instanceof ApiError && requestError.status === 401) {
          await logout().catch(() => undefined);
          navigate("/login", { replace: true });
          return;
        }
        setError(requestError);
      } finally {
        setLoading(false);
      }
  }, [user.id_employee, logout, navigate]);

  useEffect(() => { loadTrainings(); }, [loadTrainings]);

  async function handleRequest(trainingId) {
    if (submittingId !== null) return;
    setSubmittingId(trainingId);
    setFeedback("");
    try {
      await createPlannedTrainingRequest(trainingId);
      setFeedback("Votre demande a été créée et est en attente de validation.");
      await loadTrainings();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      if (requestError instanceof ApiError && requestError.status === 403) {
        setFeedback("Vous n’êtes pas autorisé à demander cette formation.");
      } else if (requestError instanceof ApiError && [404, 409, 422].includes(requestError.status) && requestError.detail) {
        setFeedback(requestError.detail);
        await loadTrainings();
      } else {
        setFeedback("La demande n’a pas pu être créée. Réessayez plus tard.");
      }
    } finally {
      setSubmittingId(null);
    }
  }

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
      {feedback && <p className="form-feedback" role="status">{feedback}</p>}

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
              <button className="button button-primary training-request-button" type="button" disabled={submittingId !== null} onClick={() => handleRequest(training.id_training)}>
                {submittingId === training.id_training ? "Envoi…" : "Demander"}
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
