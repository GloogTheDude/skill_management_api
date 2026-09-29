import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { createSkillValidation, getPendingSkillEvaluations, getSkillEvaluationWorkHistory, getValidationTypes } from "../api/skills";

function errorMessage(error) {
  if (!(error instanceof ApiError)) return "Une erreur réseau est survenue.";
  if (error.status === 403) return "Vous n’êtes pas autorisé à gérer les évaluations.";
  if ([404, 409, 422].includes(error.status) && error.detail) return error.detail;
  return "Les évaluations n’ont pas pu être chargées.";
}

function person(item) { return [item.employee_first_name, item.employee_last_name].filter(Boolean).join(" ") || `Employee #${item.id_employee}`; }
function validator(item) { return [item.validator_first_name, item.validator_last_name].filter(Boolean).join(" ") || `Validator #${item.id_validator}`; }

export default function ManageEvaluationsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const view = params.get("view") === "history" ? "history" : "pending";
  const [pending, setPending] = useState([]);
  const [history, setHistory] = useState([]);
  const [validationTypes, setValidationTypes] = useState([]);
  const [form, setForm] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [pendingData, historyData, types] = await Promise.all([getPendingSkillEvaluations(), getSkillEvaluationWorkHistory(), getValidationTypes()]);
      setPending(pendingData); setHistory(historyData); setValidationTypes(types);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(errorMessage(requestError));
    } finally { setLoading(false); }
  }, [logout, navigate]);

  useEffect(() => { if (["MANAGER", "HR"].includes(user?.permission_profile)) load(); else setLoading(false); }, [load, user]);
  const visibleHistory = useMemo(() => { const needle = query.trim().toLowerCase(); return history.filter((item) => !needle || `${person(item)} ${item.skill_name}`.toLowerCase().includes(needle)); }, [history, query]);

  function openEvaluation(item) { setForm({ item, level: "", idValidation: "", justification: "" }); setError(""); }
  async function submit(event) {
    event.preventDefault(); if (!form || saving) return; setSaving(true); setError("");
    try {
      await createSkillValidation({ id_employee: form.item.id_employee, id_skill: form.item.id_skill, level_skill: Number(form.level), id_validation: Number(form.idValidation), ...(form.justification.trim() ? { justification: form.justification.trim() } : {}) });
      setForm(null); await load();
    } catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError)); }
    finally { setSaving(false); }
  }

  if (!user || !["MANAGER", "HR"].includes(user.permission_profile)) return <div className="alert page-alert">Vous n’êtes pas autorisé à accéder à cette file.</div>;
  if (loading) return <div className="screen-state">Chargement des évaluations…</div>;
  const items = view === "pending" ? pending : visibleHistory;
  return <section><div className="page-heading"><div><p className="eyebrow">Suivi terrain</p><h1>Évaluations de compétences</h1></div></div>{error && <div className="alert page-alert">{error}</div>}<nav className="reference-tabs"><button className={`button ${view === "pending" ? "button-primary" : "button-secondary"}`} onClick={() => setParams({ view: "pending" })}>À évaluer ({pending.length})</button><button className={`button ${view === "history" ? "button-primary" : "button-secondary"}`} onClick={() => setParams({ view: "history" })}>Historique</button></nav>{view === "history" && <div className="reference-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un Employee ou une compétence…" /></div>}{items.length === 0 ? <div className="empty-state"><h2>{view === "pending" ? "Aucune compétence à évaluer" : "Aucune évaluation"}</h2><p>{view === "pending" ? "Toutes les compétences acquises visibles disposent déjà d’une évaluation courante." : "L’historique est vide."}</p></div> : <div className="reference-list">{items.map((item) => <article className="reference-card" key={view === "pending" ? `${item.id_employee}-${item.id_skill}` : item.id_skill_validation}><div><p className="reference-primary">{person(item)} — {item.skill_name}</p>{item.skill_domaine && <p>{item.skill_domaine}</p>}{view === "pending" ? <><p>Niveau acquis : {item.acquired_level}</p><p>Évaluation terrain : Non évalué</p><p>Source acquise : {item.primary_acquired_source || "Acquisition formelle"}</p></> : <><p>Niveau évalué : {item.level_skill}</p><p>{item.validated_at ? new Intl.DateTimeFormat("fr-BE").format(new Date(item.validated_at)) : "Date inconnue"} · {validator(item)}</p><p>{item.validation_type_name || "Type non renseigné"} · {item.superseded_at ? "Historique" : "Courante"}</p><p>{item.justification || "Aucune justification"}</p></>}</div>{view === "pending" && <button className="button button-primary" onClick={() => openEvaluation(item)}>Évaluer</button>}</article>)}</div>}{form && <div className="modal-backdrop"><section className="modal-panel"><h2>Évaluer {form.item.skill_name}</h2><p>{person(form.item)} · Acquis : {form.item.acquired_level}</p><form onSubmit={submit}><label>Niveau terrain<select required value={form.level} onChange={(event) => setForm({ ...form, level: event.target.value })}><option value="">Choisir</option>{[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level}</option>)}</select></label><label>Type de validation<select required value={form.idValidation} onChange={(event) => setForm({ ...form, idValidation: event.target.value })}><option value="">Choisir</option>{validationTypes.map((type) => <option key={type.id_validation} value={type.id_validation}>{type.denomination_validation || type.source || `Type ${type.id_validation}`}</option>)}</select></label><label>Justification<textarea maxLength="1000" value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} /></label><div className="card-actions"><button type="button" className="button button-secondary" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section></div>}</section>;
}
