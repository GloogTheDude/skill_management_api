import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import {
  approveTrainingRequest,
  getHrPendingTrainingRequests,
  getManagerPendingTrainingRequests,
  rejectTrainingRequest,
} from "../api/trainingRequests";
import { getAvailableTrainings } from "../api/trainings";
import { useAuth } from "../auth/AuthContext";

function formatDate(value) {
  if (!value) return "Date non renseignée";
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function displayValue(value, fallback = "Non renseigné") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function errorMessage(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 403) return "Vous n’êtes pas autorisé à traiter cette demande.";
  if ([404, 409, 422].includes(error.status) && error.detail) return error.detail;
  return fallback;
}

export default function ManageTrainingRequestsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mutationId, setMutationId] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [rejectReasons, setRejectReasons] = useState({});
  const [candidateTraining, setCandidateTraining] = useState({});
  const [candidateLoading, setCandidateLoading] = useState(null);
  const [candidateError, setCandidateError] = useState({});

  const loadRequests = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const loader = user.access_level === 3
        ? getHrPendingTrainingRequests
        : getManagerPendingTrainingRequests;
      setRequests(await loader());
      setCandidateTraining({});
      setCandidateError({});
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
  }, [user.access_level, logout, navigate]);

  useEffect(() => { loadRequests(); }, [loadRequests]);

  async function handleApprove(request) {
    if (mutationId !== null) return;
    setMutationId(request.id_training_request);
    setFeedback("");
    try {
      await approveTrainingRequest(
        request.id_training_request,
        request.id_training === null ? candidateTraining[request.id_training_request] : null,
      );
      setFeedback("La demande a été approuvée.");
      await loadRequests();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(errorMessage(requestError, "La demande n’a pas pu être approuvée."));
      if (requestError instanceof ApiError && [404, 409].includes(requestError.status)) await loadRequests();
    } finally {
      setMutationId(null);
    }
  }

  async function loadCandidates(requestId) {
    setCandidateTraining((current) => {
      const next = { ...current };
      delete next[requestId];
      delete next[`${requestId}_options`];
      return next;
    });
    setCandidateLoading(requestId);
    setCandidateError((current) => ({ ...current, [requestId]: null }));
    try {
      const trainings = await getAvailableTrainings(requests.find(
        (request) => request.id_training_request === requestId,
      )?.id_employee);
      setCandidateTraining((current) => ({ ...current, [`${requestId}_options`]: trainings }));
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setCandidateError((current) => ({
        ...current,
        [requestId]: requestError instanceof ApiError && requestError.status === 403
          ? "Vous n’êtes pas autorisé à consulter les Trainings."
          : "Impossible de charger les Trainings candidates.",
      }));
    } finally {
      setCandidateLoading(null);
    }
  }

  function selectCandidates(requestId) {
    if (candidateTraining[`${requestId}_options`]) {
      setCandidateTraining((current) => ({
        ...current,
        [requestId]: null,
        [`${requestId}_options`]: null,
      }));
      return;
    }
    loadCandidates(requestId);
  }

  async function handleReject(request) {
    if (mutationId !== null) return;
    const reason = (rejectReasons[request.id_training_request] || "").trim();
    if (!reason) {
      setFeedback("Un motif est requis pour rejeter une demande.");
      return;
    }
    setMutationId(request.id_training_request);
    setFeedback("");
    try {
      await rejectTrainingRequest(request.id_training_request, reason);
      setFeedback("La demande a été rejetée.");
      await loadRequests();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(errorMessage(requestError, "La demande n’a pas pu être rejetée."));
      if (requestError instanceof ApiError && [404, 409].includes(requestError.status)) await loadRequests();
    } finally {
      setMutationId(null);
    }
  }

  if (loading) return <div className="screen-state">Chargement des demandes à traiter…</div>;
  if (error) {
    const message = error instanceof ApiError && error.status === 403
      ? "Vous n’êtes pas autorisé à consulter cette file."
      : "Impossible de charger les demandes à traiter. Réessayez plus tard.";
    return <div className="alert page-alert" role="alert">{message}</div>;
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Manager / HR</p>
          <h1>Demandes à traiter</h1>
        </div>
        <span className="skill-count">{requests.length} demande{requests.length === 1 ? "" : "s"}</span>
      </div>
      {feedback && <p className="form-feedback" role="status">{feedback}</p>}
      {requests.length === 0 ? (
        <div className="empty-state"><h2>Aucune demande en attente</h2><p>La file de traitement est vide.</p></div>
      ) : (
        <div className="request-list">
          {requests.map((request) => {
            const personalized = request.id_training === null;
            const busy = mutationId === request.id_training_request;
            return (
              <article className="request-card" key={request.id_training_request}>
                <div className="request-card-header">
                  <div>
                    <p className="eyebrow">{personalized ? "Demande personnalisée" : "Formation planifiée"}</p>
                    <h2>{request.training_title || request.request_desc}</h2>
                    <p>{request.first_name_employee} {request.last_name_employee} · Employee #{request.id_employee}</p>
                    {request.domaine_name && <p>{request.domaine_name}</p>}
                    {!personalized && (
                      <div className="request-training-details">
                        <p><strong>Organisme :</strong> {displayValue(request.source_name)}</p>
                        <p><strong>Lieu :</strong> {displayValue(request.location)}</p>
                        <p><strong>Dates :</strong> {request.start_ || request.end_
                          ? `${formatDate(request.start_)} au ${formatDate(request.end_)}`
                          : "Non renseignées"}</p>
                        <p><strong>Durée :</strong> {request.duration_hours == null ? "Non renseignée" : `${request.duration_hours} h`}</p>
                        <p><strong>Coût horaire :</strong> {request.cost_hour == null ? "Non renseigné" : `${request.cost_hour} €/h`}</p>
                      </div>
                    )}
                  </div>
                  <span className="status-badge">{request.status}</span>
                </div>
                <p className="request-date">Demandée le {formatDate(request.requested_at)}</p>
                {personalized && <p className="request-hint">Cette demande doit être liée à une formation avant approbation.</p>}
                {personalized && (
                  <div className="request-candidate-picker">
                    <button
                      className="button button-secondary"
                      type="button"
                      onClick={() => selectCandidates(request.id_training_request)}
                      disabled={mutationId !== null || candidateLoading === request.id_training_request}
                    >
                      {candidateLoading === request.id_training_request ? "Chargement…" : "Associer une formation"}
                    </button>
                    {candidateError[request.id_training_request] && (
                      <p className="form-error" role="alert">{candidateError[request.id_training_request]}</p>
                    )}
                    {candidateTraining[`${request.id_training_request}_options`] && (
                      <>
                        <select
                          className="training-select"
                          value={candidateTraining[request.id_training_request] || ""}
                          onChange={(event) => setCandidateTraining((current) => ({
                            ...current,
                            [request.id_training_request]: event.target.value ? Number(event.target.value) : null,
                          }))}
                          disabled={mutationId !== null}
                        >
                          <option value="">Sélectionner une formation</option>
                          {candidateTraining[`${request.id_training_request}_options`].map((training) => (
                            <option key={training.id_training} value={training.id_training}>
                              {training.title} — {displayValue(training.domaine_name)}
                            </option>
                          ))}
                        </select>
                        {candidateTraining[request.id_training_request] && (() => {
                          const selected = candidateTraining[`${request.id_training_request}_options`]
                            .find((training) => training.id_training === candidateTraining[request.id_training_request]);
                          return selected ? (
                            <div className="request-training-details">
                              <p><strong>Organisme :</strong> {displayValue(selected.source_name)}</p>
                              <p><strong>Lieu :</strong> {displayValue(selected.location)}</p>
                              <p><strong>Dates :</strong> {selected.start_ || selected.end_
                                ? `${formatDate(selected.start_)} au ${formatDate(selected.end_)}`
                                : "Non renseignées"}</p>
                              <p><strong>Durée :</strong> {selected.duration_hours == null ? "Non renseignée" : `${selected.duration_hours} h`}</p>
                              <p><strong>Coût horaire :</strong> {selected.cost_hour == null ? "Non renseigné" : `${selected.cost_hour} €/h`}</p>
                            </div>
                          ) : null;
                        })()}
                      </>
                    )}
                  </div>
                )}
                <textarea
                  className="reject-reason"
                  rows="2"
                  placeholder="Motif du rejet"
                  value={rejectReasons[request.id_training_request] || ""}
                  onChange={(event) => setRejectReasons((current) => ({ ...current, [request.id_training_request]: event.target.value }))}
                  disabled={mutationId !== null}
                />
                <div className="request-actions">
                  {(!personalized || candidateTraining[request.id_training_request]) && <button className="button button-primary" type="button" onClick={() => handleApprove(request)} disabled={mutationId !== null}> {busy ? "Traitement…" : "Approuver"}</button>}
                  <button className="button button-danger" type="button" onClick={() => handleReject(request)} disabled={mutationId !== null}>{busy ? "Traitement…" : "Rejeter"}</button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
