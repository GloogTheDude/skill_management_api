import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import {
  createPersonalizedTrainingRequest,
  getMyTrainingRequests,
} from "../api/trainingRequests";
import { useAuth } from "../auth/AuthContext";

function formatDate(value) {
  if (!value) return "Date non renseignée";
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function requestErrorMessage(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 403) return "Vous n’êtes pas autorisé à effectuer cette action.";
  if ([404, 409, 422].includes(error.status) && error.detail) return error.detail;
  return fallback;
}

export default function MyTrainingRequestsPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");

  const loadRequests = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRequests(await getMyTrainingRequests());
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
  }, [logout, navigate]);

  useEffect(() => {
    loadRequests();
  }, [loadRequests]);

  async function handlePersonalizedSubmit(event) {
    event.preventDefault();
    const trimmedDescription = description.trim();
    if (!trimmedDescription || submitting) return;

    setSubmitting(true);
    setFeedback("");
    try {
      await createPersonalizedTrainingRequest(trimmedDescription);
      setDescription("");
      setFeedback("Votre demande personnalisée a été créée.");
      await loadRequests();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(requestErrorMessage(requestError, "La demande n’a pas pu être créée."));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="screen-state">Chargement de vos demandes…</div>;

  if (error) {
    const message = error instanceof ApiError && error.status === 403
      ? "Vous n’êtes pas autorisé à consulter vos demandes."
      : "Impossible de charger vos demandes. Réessayez plus tard.";
    return <div className="alert page-alert" role="alert">{message}</div>;
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Suivi personnel</p>
          <h1>Mes demandes de formation</h1>
        </div>
        <span className="skill-count">{requests.length} demande{requests.length === 1 ? "" : "s"}</span>
      </div>

      <form className="request-form" onSubmit={handlePersonalizedSubmit}>
        <div>
          <p className="eyebrow">Nouvelle demande</p>
          <h2>Demande personnalisée</h2>
        </div>
        <label htmlFor="request-description">Formation souhaitée</label>
        <textarea
          id="request-description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Décrivez la formation souhaitée"
          rows="3"
          required
        />
        <button className="button button-primary" type="submit" disabled={submitting || !description.trim()}>
          {submitting ? "Envoi…" : "Envoyer la demande"}
        </button>
        {feedback && <p className="form-feedback" role="status">{feedback}</p>}
      </form>

      {requests.length === 0 ? (
        <div className="empty-state">
          <h2>Aucune demande</h2>
          <p>Vos demandes de formation apparaîtront ici.</p>
        </div>
      ) : (
        <div className="request-list">
          {requests.map((request) => (
            <article className="request-card" key={request.id_training_request}>
              <div className="request-card-header">
                <div>
                  <p className="eyebrow">{request.training_title ? "Formation planifiée" : "Demande personnalisée"}</p>
                  <h2>{request.training_title || request.request_desc}</h2>
                  {request.domaine_name && <p>{request.domaine_name}</p>}
                </div>
                <span className="status-badge">{request.status}</span>
              </div>
              <p className="request-date">Demandée le {formatDate(request.requested_at)}</p>
              {request.reason && <p className="request-reason">Motif : {request.reason}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
