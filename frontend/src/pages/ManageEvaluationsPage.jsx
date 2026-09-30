import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { createSkillValidationBatch, getEmployeeSkillProfile, getSkillEvaluationWorkHistory, getValidationTypes } from "../api/skills";

function person(item) { return [item.employee_first_name, item.employee_last_name].filter(Boolean).join(" ") || `Employee #${item.id_employee}`; }
function validator(item) { return [item.validator_first_name, item.validator_last_name].filter(Boolean).join(" ") || `Validator #${item.id_validator}`; }
function errorMessage(error) { if (!(error instanceof ApiError)) return "Une erreur réseau est survenue."; if (error.status === 403) return "Vous n’êtes pas autorisé à gérer les évaluations."; return error.detail || "Les évaluations n’ont pas pu être chargées."; }

export default function ManageEvaluationsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { idEmployee } = useParams();
  const [history, setHistory] = useState([]);
  const [types, setTypes] = useState([]);
  const [profile, setProfile] = useState([]);
  const [form, setForm] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const loadQueue = useCallback(async () => {
    setLoading(true); setError("");
    try { const [historyData, validationTypes] = await Promise.all([getSkillEvaluationWorkHistory(), getValidationTypes()]); setHistory(historyData); setTypes(validationTypes); }
    catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError)); }
    finally { setLoading(false); }
  }, [logout, navigate]);
  useEffect(() => { if (!["MANAGER", "HR"].includes(user?.permission_profile)) { setLoading(false); return; } if (!idEmployee) loadQueue(); }, [idEmployee, loadQueue, user]);
  useEffect(() => { if (!idEmployee) return; setLoading(true); Promise.all([getEmployeeSkillProfile(Number(idEmployee)), getValidationTypes()]).then(([skills, validationTypes]) => { setProfile(skills); setTypes(validationTypes); }).catch((requestError) => setError(errorMessage(requestError))).finally(() => setLoading(false)); }, [idEmployee]);
  const visibleHistory = useMemo(() => { const needle = query.trim().toLowerCase(); return history.filter((item) => !needle || `${person(item)} ${item.skill_name}`.toLowerCase().includes(needle)); }, [history, query]);
  function openForm() { setForm({ levels: {}, idValidation: "", justification: "" }); setError(""); }
  function updateLevel(skillId, value) { setForm((current) => ({ ...current, levels: { ...current.levels, [skillId]: value } })); }
  async function submit(event) { event.preventDefault(); if (!form || saving) return; const evaluations = Object.entries(form.levels).filter(([, level]) => level !== "").map(([idSkill, level]) => ({ id_skill: Number(idSkill), level_skill: Number(level) })); if (!evaluations.length || !form.idValidation) return; setSaving(true); setError(""); try { await createSkillValidationBatch({ id_employee: Number(idEmployee), id_validation: Number(form.idValidation), ...(form.justification.trim() ? { justification: form.justification.trim() } : {}), evaluations }); setForm(null); const skills = await getEmployeeSkillProfile(Number(idEmployee)); setProfile(skills); await loadQueue(); } catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError)); } finally { setSaving(false); } }
  if (!user || !["MANAGER", "HR"].includes(user.permission_profile)) return <div className="alert page-alert">Vous n’êtes pas autorisé à accéder à cette file.</div>;
  if (loading) return <div className="screen-state">Chargement des évaluations…</div>;
  if (idEmployee) return <section><button className="button button-secondary" type="button" onClick={() => navigate("/app/manage-evaluations")}>← Retour aux Employees</button><div className="page-heading"><div><p className="eyebrow">Évaluation de compétences</p><h1>Employee #{idEmployee}</h1></div></div>{error && <div className="alert page-alert">{error}</div>}<div className="reference-list">{profile.map((skill) => <article className="reference-card" key={skill.skill_id}><div><p className="reference-primary">{skill.skill_name}</p>{skill.skill_domaine && <p>{skill.skill_domaine}</p>}<p>Niveau acquis : {skill.acquired_level ?? "Aucun"}</p><p>Niveau évalué : {skill.evaluated_level ?? "Non évalué"}</p></div><select aria-label={`Niveau évalué pour ${skill.skill_name}`} value={form?.levels?.[skill.skill_id] || ""} onChange={(event) => { if (!form) openForm(); updateLevel(skill.skill_id, event.target.value); }}><option value="">Ne pas modifier</option>{[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level}</option>)}</select></article>)}</div><button className="button button-primary" type="button" onClick={openForm} disabled={!profile.length}>Enregistrer les évaluations</button>{form && <div className="modal-backdrop"><section className="modal-panel"><h2>Valider les compétences sélectionnées</h2><form onSubmit={submit}><label>Type de validation<select required value={form.idValidation} onChange={(event) => setForm({ ...form, idValidation: event.target.value })}><option value="">Choisir</option>{types.map((type) => <option key={type.id_validation} value={type.id_validation}>{type.denomination_validation || type.source || `Type ${type.id_validation}`}</option>)}</select></label><label>Justification commune<textarea maxLength="1000" value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} /></label><div className="card-actions"><button type="button" className="button button-secondary" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section></div>}</section>;
  return <section><div className="page-heading"><div><p className="eyebrow">Suivi des évaluations</p><h1>Historique des évaluations</h1></div></div>{error && <div className="alert page-alert">{error}</div>}<div className="reference-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un Employee ou une compétence…" /></div><div className="reference-list">{visibleHistory.map((item) => <article className="reference-card" key={item.id_skill_validation}><div><p className="reference-primary">{person(item)} — {item.skill_name}</p><p>Niveau évalué : {item.level_skill}</p><p>{item.validation_type_name || "Type non renseigné"} · {validator(item)}</p><p>{item.superseded_at ? "Historique" : "Courante"}</p></div></article>)}</div></section>;
}
