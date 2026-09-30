import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import {
  closeParticipation,
  cancelParticipation,
  deleteParticipationDocument,
  downloadParticipationDocument,
  getCompletableParticipations,
  getParticipationDocuments,
  getParticipations,
  startParticipation,
  uploadParticipationDocument,
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

const terminalStatuses = new Set(["COMPLETED", "FAILED", "ABSENT", "CANCELLED"]);

function todayKey() {
  const today = new Date();
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
}

function trainingState(participation, today = todayKey()) {
  if (participation.end_ && participation.end_ < today) return "past";
  if (participation.start_ && participation.start_ > today) return "upcoming";
  return "current";
}

export default function ParticipationsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [participations, setParticipations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [completable, setCompletable] = useState(new Set());
  const [mutationKey, setMutationKey] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [results, setResults] = useState({});
  const [documents, setDocuments] = useState({});
  const [documentLoading, setDocumentLoading] = useState(null);
  const [documentForm, setDocumentForm] = useState({});
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState("");
  const requestedView = searchParams.get("view");
  const allowedViews = useMemo(() => user.permission_profile === "HR" ? ["current", "to-close", "history"] : ["current", "history"], [user.permission_profile]);
  const view = allowedViews.includes(requestedView) ? requestedView : "current";
  const query = searchParams.get("q") || "";
  const dateFrom = searchParams.get("from") || "";
  const dateTo = searchParams.get("to") || "";
  const resultFilter = searchParams.get("result") || "";

  useEffect(() => () => {
    if (preview?.url) window.URL.revokeObjectURL(preview.url);
  }, [preview]);

  useEffect(() => {
    if (!preview) return undefined;
    function closeOnEscape(event) {
      if (event.key === "Escape") setPreview(null);
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [preview]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const participationResult = await getParticipations();
      let completableResult = [];
      if (user.permission_profile === "HR") {
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
  }, [logout, navigate, user.permission_profile]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (requestedView && !allowedViews.includes(requestedView)) {
      const next = new window.URLSearchParams(searchParams);
      next.set("view", "current");
      setSearchParams(next, { replace: true });
    }
  }, [allowedViews, requestedView, searchParams, setSearchParams]);

  function updateFilters(changes) {
    const next = new window.URLSearchParams(searchParams);
    Object.entries(changes).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    setSearchParams(next, { replace: true });
  }

  function selectView(nextView) { updateFilters({ view: nextView }); }

  const filteredParticipations = participations.filter((participation) => {
    const state = trainingState(participation);
    const isToClose = completable.has(`${participation.id_employee}-${participation.id_training}`);
    const isHistory = terminalStatuses.has(participation.status);
    if (view === "to-close" && !isToClose) return false;
    if (view === "history" && !isHistory) return false;
    if (view === "current" && (isHistory || (user.permission_profile === "HR" && state === "past"))) return false;
    const searchable = `${participation.employee_first_name || ""} ${participation.employee_last_name || ""}`.toLocaleLowerCase("fr");
    if (query && !searchable.includes(query.toLocaleLowerCase("fr"))) return false;
    if (dateFrom && participation.end_ && participation.end_ < dateFrom) return false;
    if (dateTo && participation.start_ && participation.start_ > dateTo) return false;
    if (view === "history" && resultFilter && participation.status !== resultFilter) return false;
    return true;
  });

  async function handleClose(participation) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    const result = results[key];
    if (mutationKey !== null) return;
    if (!result) return;
    setMutationKey(key);
    setFeedback("");
    try {
      await closeParticipation(participation.id_employee, participation.id_training, result);
      setFeedback("La participation a été clôturée.");
      setResults((current) => ({ ...current, [key]: "" }));
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

  async function handleCancel(participation) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    if (mutationKey !== null) return;
    setMutationKey(key);
    setFeedback("");
    try {
      await cancelParticipation(participation.id_employee, participation.id_training);
      setFeedback("La participation a été annulée.");
      await loadData();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(requestError instanceof ApiError && requestError.detail
        ? requestError.detail
        : "La participation n’a pas pu être annulée.");
      if (requestError instanceof ApiError && [404, 409].includes(requestError.status)) await loadData();
    } finally {
      setMutationKey(null);
    }
  }

  async function handleStart(participation) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    if (mutationKey !== null) return;
    setMutationKey(key);
    setFeedback("");
    try {
      await startParticipation(participation.id_employee, participation.id_training);
      setFeedback("La participation a démarré.");
      await loadData();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(requestError instanceof ApiError && requestError.detail
        ? requestError.detail
        : "La participation n’a pas pu démarrer.");
      if (requestError instanceof ApiError && [404, 409].includes(requestError.status)) await loadData();
    } finally {
      setMutationKey(null);
    }
  }

  async function loadDocuments(participation) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    setDocumentLoading(key);
    try {
      const result = await getParticipationDocuments(participation.id_employee, participation.id_training);
      setDocuments((current) => ({ ...current, [key]: result }));
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setFeedback(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à consulter ces documents."
        : "Impossible de charger les documents.");
    } finally {
      setDocumentLoading(null);
    }
  }

  async function handleUpload(participation) {
    const key = `${participation.id_employee}-${participation.id_training}`;
    const form = documentForm[key];
    if (!form?.file || !form.documentType) return;
    setDocumentLoading(key);
    try {
      await uploadParticipationDocument(
        participation.id_employee,
        participation.id_training,
        form.documentType,
        form.file,
      );
      setDocumentForm((current) => ({ ...current, [key]: { documentType: "", file: null } }));
      await loadDocuments(participation);
      setFeedback("Le document a été ajouté.");
    } catch (requestError) {
      setFeedback(requestError instanceof ApiError && requestError.detail
        ? requestError.detail
        : "Le document n’a pas pu être ajouté.");
    } finally {
      setDocumentLoading(null);
    }
  }

  async function handleDownload(document) {
    try {
      const blob = await downloadParticipationDocument(document.id_participation_document);
      const url = window.URL.createObjectURL(blob);
      const link = window.document.createElement("a");
      link.href = url;
      link.download = document.original_filename;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      setFeedback(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à télécharger ce document."
        : "Le téléchargement a échoué.");
    }
  }

  async function handlePreview(document) {
    if (preview?.url) window.URL.revokeObjectURL(preview.url);
    setPreview(null);
    setPreviewError("");
    setPreviewLoading(true);
    try {
      const blob = await downloadParticipationDocument(document.id_participation_document);
      setPreview({ document, url: window.URL.createObjectURL(blob) });
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setPreviewError(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à consulter ce document."
        : requestError instanceof ApiError && requestError.status === 404
          ? "Ce document n’est plus disponible."
          : "La prévisualisation a échoué.");
    } finally {
      setPreviewLoading(false);
    }
  }

  async function handleDelete(document, participation) {
    try {
      await deleteParticipationDocument(document.id_participation_document);
      await loadDocuments(participation);
      setFeedback("Le document a été supprimé.");
    } catch {
      setFeedback("Le document n’a pas pu être supprimé.");
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
        <span className="skill-count">{filteredParticipations.length} participation{filteredParticipations.length === 1 ? "" : "s"}</span>
      </div>
      {feedback && <p className="form-feedback" role="status">{feedback}</p>}
      <div className="participation-tabs" role="tablist" aria-label="Vues des participations">
        <button className={`button ${view === "current" ? "button-primary" : "button-secondary"}`} onClick={() => selectView("current")} role="tab" aria-selected={view === "current"}>Actuelles</button>
        {user.permission_profile === "HR" && <button className={`button ${view === "to-close" ? "button-primary" : "button-secondary"}`} onClick={() => selectView("to-close")} role="tab" aria-selected={view === "to-close"}>À clôturer ({completable.size})</button>}
        <button className={`button ${view === "history" ? "button-primary" : "button-secondary"}`} onClick={() => selectView("history")} role="tab" aria-selected={view === "history"}>Historique</button>
      </div>
      <div className="participation-filters">
        {(user.permission_profile !== "EMPLOYEE" || view === "history") && <label>Recherche nom / prénom<input value={query} onChange={(event) => updateFilters({ q: event.target.value })} placeholder="Ex. Dupont" /></label>}
        <label>Du<input type="date" value={dateFrom} onChange={(event) => updateFilters({ from: event.target.value })} /></label>
        <label>Au<input type="date" value={dateTo} onChange={(event) => updateFilters({ to: event.target.value })} /></label>
        {view === "history" && <label>Résultat<select value={resultFilter} onChange={(event) => updateFilters({ result: event.target.value })}><option value="">Tous</option><option value="COMPLETED">Réussite</option><option value="FAILED">Échec</option><option value="ABSENT">Absent</option><option value="CANCELLED">Annulée</option></select></label>}
        <button className="button button-secondary" type="button" onClick={() => updateFilters({ q: "", from: "", to: "", result: "" })}>Réinitialiser les filtres</button>
      </div>
      {filteredParticipations.length === 0 ? (
        <div className="empty-state"><h2>{view === "to-close" ? "Aucune participation à clôturer" : view === "history" ? "Aucune participation dans l’historique" : participations.length ? "Aucun résultat pour ces filtres" : "Aucune participation actuelle"}</h2><p>{participations.length ? "Modifiez les filtres ou réinitialisez-les." : "Aucune participation ne correspond à cette vue."}</p></div>
      ) : (
        <div className="request-list">
          {filteredParticipations.map((participation) => {
            const key = `${participation.id_employee}-${participation.id_training}`;
            const busy = mutationKey === key;
            const canClose = completable.has(key);
            const visualStatus = view === "to-close"
              ? "À clôturer"
              : view === "history"
                ? statusLabels[participation.status] || participation.status
                : participation.status === "REGISTERED"
              && participation.start_
              && new Date(`${participation.start_}T00:00:00`) <= new Date()
              && (!participation.end_ || new Date(`${participation.end_}T00:00:00`) >= new Date())
              ? "En cours"
              : participation.end_ && participation.end_ < todayKey() && !terminalStatuses.has(participation.status)
                ? "Résultat en attente"
                : statusLabels[participation.status] || participation.status;
            return (
            <article className="request-card" key={`${participation.id_employee}-${participation.id_training}`}>
              <div className="request-card-header">
                <div>
                  <p className="eyebrow">Participation</p>
                  <h2>{displayValue(participation.training_title)}</h2>
                  {user.permission_profile !== "EMPLOYEE" && (
                    <p>{displayValue(participation.employee_first_name)} {displayValue(participation.employee_last_name)}</p>
                  )}
                </div>
                <span className="status-badge">{visualStatus}</span>
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
              <div className="participation-documents">
                <button className="button button-secondary" type="button" onClick={() => loadDocuments(participation)} disabled={documentLoading === key}>
                  {documentLoading === key ? "Chargement…" : "Documents"}
                </button>
                {documents[key] && (
                  <div>
                    <p><strong>Documents ({documents[key].length})</strong></p>
                    {documents[key].map((document) => (
                      <p key={document.id_participation_document}>
                        {document.document_type} — {document.original_filename}{" "}
                        {["application/pdf", "image/png", "image/jpeg", "image/webp"].includes(document.mime_type) && (
                          <button className="button button-secondary" type="button" onClick={() => handlePreview(document)}>Voir</button>
                        )}{" "}
                        <button className="button button-secondary" type="button" onClick={() => handleDownload(document)}>Télécharger</button>
                        {user.permission_profile === "HR" && <button className="button button-danger" type="button" onClick={() => handleDelete(document, participation)}>Supprimer</button>}
                      </p>
                    ))}
                    {user.permission_profile === "HR" && (
                      <div className="request-actions">
                        <select
                          className="training-select"
                          value={documentForm[key]?.documentType || ""}
                          onChange={(event) => setDocumentForm((current) => ({ ...current, [key]: { ...current[key], documentType: event.target.value } }))}
                        >
                          <option value="">Type de document</option>
                          <option value="CERTIFICATE">Certificat</option>
                          <option value="DIPLOMA">Diplôme</option>
                          <option value="ATTENDANCE_CERTIFICATE">Attestation de présence</option>
                          <option value="OTHER">Autre</option>
                        </select>
                        <input type="file" accept="application/pdf,image/jpeg,image/png" onChange={(event) => setDocumentForm((current) => ({ ...current, [key]: { ...current[key], file: event.target.files?.[0] || null } }))} />
                        <button className="button button-primary" type="button" onClick={() => handleUpload(participation)} disabled={documentLoading === key}>Ajouter</button>
                      </div>
                    )}
                  </div>
                )}
              </div>
              {user.permission_profile === "HR" && canClose && (
                <div className="request-actions">
                  <select
                    className="training-select"
                    value={results[key] || ""}
                    onChange={(event) => setResults((current) => ({ ...current, [key]: event.target.value }))}
                    disabled={mutationKey !== null}
                  >
                    <option value="">Résultat de la formation</option>
                    <option value="COMPLETED">Réussite</option>
                    <option value="FAILED">Échec</option>
                    <option value="ABSENT">Absent</option>
                  </select>
                  <button className="button button-primary" type="button" onClick={() => handleClose(participation)} disabled={mutationKey !== null || !results[key]}>
                    {busy ? "Clôture…" : "Clôturer"}
                  </button>
                </div>
              )}
              {user.permission_profile === "HR"
                && ["REGISTERED", "IN_PROGRESS"].includes(participation.status)
                && (!participation.end_ || new Date(`${participation.end_}T00:00:00`) > new Date()) && (
                <div className="request-actions">
                  <button className="button button-danger" type="button" onClick={() => handleCancel(participation)} disabled={mutationKey !== null}>
                    {busy ? "Annulation…" : "Annuler"}
                  </button>
                </div>
              )}
              {user.permission_profile === "HR" && participation.status === "REGISTERED" && (
                <div className="request-actions">
                  <button className="button button-secondary" type="button" onClick={() => handleStart(participation)} disabled={mutationKey !== null}>
                    {busy ? "Démarrage…" : "Démarrer"}
                  </button>
                </div>
              )}
              {user.permission_profile === "HR" && participation.status === "REGISTERED" && !canClose && participation.end_ && new Date(`${participation.end_}T00:00:00`) < new Date() && (
                <p className="request-hint">Formation terminée, en attente de clôture.</p>
              )}
            </article>
            );
          })}
        </div>
      )}
      {(previewLoading || previewError || preview) && (
        <div className="document-preview-backdrop" role="presentation" onClick={() => setPreview(null)}>
          <div className="document-preview-modal" role="dialog" aria-modal="true" aria-labelledby="document-preview-title" onClick={(event) => event.stopPropagation()}>
            <div className="document-preview-header">
              <h2 id="document-preview-title">{preview?.document.original_filename || "Prévisualisation"}</h2>
              <button className="button button-secondary" type="button" onClick={() => setPreview(null)}>Fermer</button>
            </div>
            {previewLoading && <p className="screen-state">Chargement de la prévisualisation…</p>}
            {previewError && <p className="form-error" role="alert">{previewError}</p>}
            {preview?.document.mime_type === "application/pdf" && <iframe className="document-preview-frame" src={preview.url} title={preview.document.original_filename} />}
            {preview && preview.document.mime_type.startsWith("image/") && <img className="document-preview-image" src={preview.url} alt={preview.document.original_filename} />}
          </div>
        </div>
      )}
    </section>
  );
}
