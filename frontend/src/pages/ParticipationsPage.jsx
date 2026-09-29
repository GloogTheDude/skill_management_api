import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import {
  completeParticipation,
  getCompletableParticipations,
  getParticipations,
  startParticipation,
} from "../api/participations";
import { useAuth } from "../auth/AuthContext";

const statusLabels = {
  REGISTERED: "Inscrit",
  IN_PROGRESS: "En cours",
  COMPLETED: "Terminée",
  FAILED: "Échec",
  ABSENT: "Absent",
  CANCELLED: "Annulée",
};

function formatDate(value) {
  if (!value) return "Non renseignée";
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function displayValue(value) {
  return value === null || value === undefined || value === "" ? "Non renseigné" : value;
}

export default function ParticipationsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [participations, setParticipations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [completable, setCompletable] = useState(new Set());
  const [mutationKey, setMutationKey] = useState(null);
  const [feedback, setFeedback] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const participationResult = await getParticipations();
      let completableResult = [];
      if (user.access_level === 3) {
        completableResult = await getCompletableParticipations();
      }
      setParticipations(participationResult);
      setCompletable(new Set(completableResult.map((item) => `${item.id_employee}-${item.id_training}`)));
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
  }, [logout, navigate, user.access_level]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleTransition(participation, transition) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    if (mutationKey !== null) return;
    setMutationKey(key);
    setFeedback("");
    try {
      if (transition === "start") {
        await startParticipation(participation.id_employee, participation.id_training);
        setFeedback("La participation a été démarrée.");
      } else {
        await completeParticipation(participation.id_employee, participation.id_training);
        setFeedback("La participation a été terminée.");
      }
      await loadData();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      const detail = requestError instanceof ApiError && requestError.detail;
      setFeedback(detail || "La transition de participation a échoué. Réessayez plus tard.");
      if (requestError instanceof ApiError && [404, 409].includes(requestError.status)) {
        await loadData();
      }
    } finally {
      setMutationKey(null);
    }
  }

  if (loading) return <div className="screen-state">Chargement des participations…</div>;
  if (error) {
    const message = error instanceof ApiError && error.status === 403
      ? "Vous n’êtes pas autorisé à consulter ces participations."
      : "Impossible de charger les participations. Réessayez plus tard.";
    return <div className="alert page-alert" role="alert">{message}</div>;
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">Formation</p><h1>Participations</h1></div>
        <span className="skill-count">{participations.length} participation{participations.length === 1 ? "" : "s"}</span>
      </div>
      {feedback && <p className="form-feedback" role="status">{feedback}</p>}
      {participations.length === 0 ? (
        <div className="empty-state"><h2>Aucune participation</h2><p>Vous n’avez pas encore de participation enregistrée.</p></div>
      ) : (
        <div className="request-list">
          {participations.map((participation) => {
            const key = `${participation.id_employee}-${participation.id_training}`;
            const busy = mutationKey === key;
            const canComplete = completable.has(key);
            return (
            <article className="request-card" key={`${participation.id_employee}-${participation.id_training}`}>
              <div className="request-card-header">
                <div>
                  <p className="eyebrow">Participation</p>
                  <h2>{displayValue(participation.training_title)}</h2>
                  {user.access_level !== 1 && (
                    <p>{displayValue(participation.employee_first_name)} {displayValue(participation.employee_last_name)}</p>
                  )}
                </div>
                <span className="status-badge">{statusLabels[participation.status] || participation.status}</span>
              </div>
              <div className="participation-details">
                <p><strong>Organisme :</strong> {displayValue(participation.source_name)}</p>
                <p><strong>Domaine :</strong> {displayValue(participation.domaine_name)}</p>
                <p><strong>Lieu :</strong> {displayValue(participation.location)}</p>
                <p><strong>Dates :</strong> {participation.start_ || participation.end_
                  ? `${formatDate(participation.start_)} au ${formatDate(participation.end_)}`
                  : "Non renseignées"}</p>
                <p><strong>Durée :</strong> {participation.duration_hours == null ? "Non renseignée" : `${participation.duration_hours} h`}</p>
                <p><strong>Coût horaire :</strong> {participation.cost_hour == null ? "Non renseigné" : `${participation.cost_hour} €/h`}</p>
              </div>
              {user.access_level === 3 && participation.status === "REGISTERED" && (
                <div className="request-actions">
                  <button className="button button-primary" type="button" onClick={() => handleTransition(participation, "start")} disabled={mutationKey !== null}>
                    {busy ? "Démarrage…" : "Démarrer"}
                  </button>
                </div>
              )}
              {user.access_level === 3 && participation.status === "IN_PROGRESS" && canComplete && (
                <div className="request-actions">
                  <button className="button button-primary" type="button" onClick={() => handleTransition(participation, "complete")} disabled={mutationKey !== null}>
                    {busy ? "Finalisation…" : "Terminer"}
                  </button>
                </div>
              )}
              {user.access_level === 3 && participation.status === "IN_PROGRESS" && !canComplete && (
                <p className="request-hint">Formation non terminée.</p>
              )}
            </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
