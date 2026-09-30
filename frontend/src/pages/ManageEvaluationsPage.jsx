import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { getEmployee } from "../api/employees";
import { createSkillValidationBatch, getAllSkills, getEmployeeSkillProfile, getSkillEvaluationWorkHistory, getValidationTypes } from "../api/skills";

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
  const [availableSkills, setAvailableSkills] = useState([]);
  const [employee, setEmployee] = useState(null);
  const [form, setForm] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");

  const loadHistory = useCallback(async () => {
    setLoading(true); setError("");
    try { const [historyData, validationTypes] = await Promise.all([getSkillEvaluationWorkHistory(), getValidationTypes()]); setHistory(historyData); setTypes(validationTypes); }
    catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError)); }
    finally { setLoading(false); }
  }, [logout, navigate]);

  useEffect(() => { if (!user || !["MANAGER", "HR"].includes(user.permission_profile)) { setLoading(false); return; } if (!idEmployee) loadHistory(); }, [idEmployee, loadHistory, user]);
  useEffect(() => {
    if (!idEmployee) return;
    setLoading(true); setError("");
    Promise.all([getEmployee(Number(idEmployee)), getEmployeeSkillProfile(Number(idEmployee)), getValidationTypes(), getAllSkills()])
      .then(([employeeData, skills, validationTypes, allSkills]) => { setEmployee(employeeData); setProfile(skills); setTypes(validationTypes); setAvailableSkills(allSkills); if (!skills.length) setForm({ levels: {}, idValidation: "", justification: "" }); })
      .catch((requestError) => setError(errorMessage(requestError)))
      .finally(() => setLoading(false));
  }, [idEmployee]);

  const visibleHistory = useMemo(() => { const needle = query.trim().toLowerCase(); return history.filter((item) => !needle || `${person(item)} ${item.skill_name}`.toLowerCase().includes(needle)); }, [history, query]);
  function openForm(skillId = null) { setForm({ levels: skillId ? { [skillId]: "" } : {}, idValidation: "", justification: "" }); setError(""); setFeedback(""); }
  function updateLevel(skillId, value) { setForm((current) => ({ ...current, levels: { ...current.levels, [skillId]: value } })); }
  function cancelSkill(skillId) { setForm((current) => { const levels = { ...current.levels }; delete levels[skillId]; return { ...current, levels }; }); }
  function addSkill(skillId) { if (skillId) updateLevel(skillId, ""); }
  async function submit(event) {
    event.preventDefault(); if (!form || saving) return;
    const evaluations = Object.entries(form.levels).filter(([, level]) => level !== "").map(([idSkill, level]) => ({ id_skill: Number(idSkill), level_skill: Number(level) }));
    if (!evaluations.length || !form.idValidation) return;
    setSaving(true); setError("");
    try { await createSkillValidationBatch({ id_employee: Number(idEmployee), id_validation: Number(form.idValidation), ...(form.justification.trim() ? { justification: form.justification.trim() } : {}), evaluations }); setForm(null); setProfile(await getEmployeeSkillProfile(Number(idEmployee))); setFeedback(`${evaluations.length} évaluation${evaluations.length === 1 ? "" : "s"} enregistrée${evaluations.length === 1 ? "" : "s"}.`); }
    catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError)); }
    finally { setSaving(false); }
  }

  if (!user || !["MANAGER", "HR"].includes(user.permission_profile)) return <div className="alert page-alert">Vous n’êtes pas autorisé à accéder à cette file.</div>;
  if (loading) return <div className="screen-state">Chargement des évaluations…</div>;
  if (!idEmployee) return <section><div className="page-heading"><div><p className="eyebrow">Suivi des évaluations</p><h1>Historique des évaluations</h1></div></div>{error && <div className="alert page-alert">{error}</div>}<div className="reference-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un Employee ou une compétence…" /></div><div className="reference-list">{visibleHistory.map((item) => <article className="reference-card" key={item.id_skill_validation}><div><p className="reference-primary">{person(item)} — {item.skill_name}</p><p>Niveau évalué : {item.level_skill}</p><p>{item.validation_type_name || "Type non renseigné"} · {validator(item)}</p><p>{item.superseded_at ? "Historique" : "Courante"}</p></div></article>)}</div></section>;

  const selectedCount = form ? Object.values(form.levels).filter(Boolean).length : 0;
  const addedSkills = form ? Object.keys(form.levels).filter((id) => !profile.some((skill) => skill.skill_id === Number(id))).map((id) => availableSkills.find((skill) => skill.id_skill === Number(id))).filter(Boolean) : [];
  return <section className="evaluation-page"><button className="button button-secondary" type="button" onClick={() => navigate("/app/team")}>← Retour à la liste</button><div className="page-heading"><div><p className="eyebrow">Évaluation de compétences</p><h1>Évaluation de {[employee?.first_name, employee?.last_name].filter(Boolean).join(" ") || `Employee #${idEmployee}`}</h1>{employee?.denomination_role && <p>{employee.denomination_role}</p>}</div></div>{error && <div className="alert page-alert">{error}</div>}{feedback && <p className="form-feedback" role="status">{feedback}</p>}<div className="reference-list evaluation-skills">{profile.map((skill) => { const selected = Boolean(form?.levels && Object.prototype.hasOwnProperty.call(form.levels, skill.skill_id)); return <article className="reference-card evaluation-skill-card" key={skill.skill_id}><div><p className="reference-primary">{skill.skill_name}</p>{skill.skill_domaine && <p>{skill.skill_domaine}</p>}<p>Niveau acquis : {skill.acquired_level ?? "—"}{skill.acquired_level !== null && skill.acquired_level !== undefined ? " / 5" : ""}</p><p>Niveau évalué actuel : {skill.evaluated_level ?? "Non évalué"}{skill.evaluated_level !== null && skill.evaluated_level !== undefined ? " / 5" : ""}</p>{selected && <label>Nouveau niveau<select aria-label={`Nouveau niveau pour ${skill.skill_name}`} required value={form.levels[skill.skill_id]} onChange={(event) => updateLevel(skill.skill_id, event.target.value)}><option value="">Choisir</option>{[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level} / 5</option>)}</select></label>}</div>{selected ? <button className="button button-secondary" type="button" onClick={() => cancelSkill(skill.skill_id)}>Annuler cette évaluation</button> : <button className="button button-primary" type="button" onClick={() => openForm(skill.skill_id)}>Évaluer</button>}</article>; })}</div>{form && <section className="evaluation-form"><h2>Informations de l’évaluation</h2><label>Type d’évaluation<select required value={form.idValidation} onChange={(event) => setForm({ ...form, idValidation: event.target.value })}><option value="">Choisir</option>{types.map((type) => <option key={type.id_validation} value={type.id_validation}>{type.denomination_validation || type.source || `Type ${type.id_validation}`}</option>)}</select></label><label>Justification / commentaire<textarea maxLength="1000" value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} /></label><h3>Compétences évaluées : {selectedCount}</h3>{addedSkills.map((skill) => <div className="added-evaluation-skill" key={skill.id_skill}><strong>{skill.name_skill}</strong><select aria-label={`Niveau pour ${skill.name_skill}`} required value={form.levels[skill.id_skill]} onChange={(event) => updateLevel(skill.id_skill, event.target.value)}><option value="">Choisir un niveau</option>{[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level} / 5</option>)}</select><button type="button" className="button button-secondary" onClick={() => cancelSkill(skill.id_skill)}>Retirer</button></div>)}<button className="button button-primary" type="button" disabled={!selectedCount || saving} onClick={submit}>{saving ? "Enregistrement…" : `Enregistrer ${selectedCount} évaluation${selectedCount === 1 ? "" : "s"}`}</button><label className="add-evaluation-skill">Ajouter une compétence observée<select value="" onChange={(event) => addSkill(event.target.value)}><option value="">Choisir une Skill</option>{availableSkills.filter((skill) => !profile.some((item) => item.skill_id === skill.id_skill) && !Object.prototype.hasOwnProperty.call(form.levels, skill.id_skill)).map((skill) => <option key={skill.id_skill} value={skill.id_skill}>{skill.name_skill} — {skill.name_domaine || "Domaine non renseigné"}</option>)}</select></label></section>}</section>;
}
