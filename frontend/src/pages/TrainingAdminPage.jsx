import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { archiveTraining, createTraining, getTrainingSkills, getTrainings, updateTraining } from "../api/trainings";
import { getCertifications, getDiplomas, getDomaines, getSkills, getTrainingSources } from "../api/references";
import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

const blank = { title: "", id_domaine: "", id_source: "", location: "", start_: "", end_: "", duration_hours: "", cost_hour: "", mode: "skills", id_diploma: "", id_certification: "", skills: [] };

function errorMessage(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 403) return "Accès refusé.";
  if ([409, 422].includes(error.status) && error.detail) return error.detail;
  if (error.status === 404) return "La ressource demandée n'existe plus.";
  return fallback;
}

function dateLabel(value) {
  return value ? new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`)) : "Non renseignée";
}

function valueLabel(value) { return value === null || value === undefined || value === "" ? "Non renseigné" : value; }

function todayKey() {
  const today = new Date();
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
}

function temporalStatus(training, today = todayKey()) {
  if (training.end_ && training.end_ < today) return { key: "past", label: "Terminée" };
  if (training.start_ && training.start_ > today) return { key: "upcoming", label: "À venir" };
  if (training.start_ && training.end_ && training.start_ <= today && training.end_ >= today) return { key: "current", label: "En cours" };
  return { key: "unknown", label: "Dates à préciser" };
}

export default function TrainingAdminPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [trainings, setTrainings] = useState([]);
  const [refs, setRefs] = useState({ domaines: [], sources: [], skills: [], diplomas: [], certifications: [] });
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [view, setView] = useState("active");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [items, domaines, sources, skills, diplomas, certifications] = await Promise.all([
        getTrainings(), getDomaines(), getTrainingSources(), getSkills(), getDiplomas(), getCertifications(),
      ]);
      setTrainings(items);
      setRefs({ domaines, sources, skills, diplomas, certifications });
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(errorMessage(requestError, "Les données Training n'ont pas pu être chargées."));
    } finally { setLoading(false); }
  }, [logout, navigate]);

  useEffect(() => { load(); }, [load]);

  const groupedTrainings = trainings.reduce((groups, training) => {
    const status = temporalStatus(training);
    groups[status.key] = [...(groups[status.key] || []), { training, status }];
    return groups;
  }, {});
  const sortByStart = (left, right) => (left.training.start_ || "9999-99-99").localeCompare(right.training.start_ || "9999-99-99");
  const activeTrainings = [...(groupedTrainings.current || []), ...(groupedTrainings.upcoming || []).sort(sortByStart), ...(groupedTrainings.unknown || [])];
  const historicalTrainings = (groupedTrainings.past || []).sort(sortByStart);

  function openCreate() { setFeedback(""); setError(""); setForm({ ...blank, skills: [] }); }

  async function openEdit(training) {
    setFeedback(""); setError("");
    const mode = training.diploma_name ? "diploma" : training.certification_name ? "certification" : "skills";
    let skills = [];
    if (mode === "skills") {
      try { skills = (await getTrainingSkills()).filter((item) => item.id_training === training.id_training).map((item) => ({ id_skill: item.id_skill, level: item.granted_level })); }
      catch (requestError) { setError(errorMessage(requestError, "Les compétences de la formation n'ont pas pu être chargées.")); return; }
    }
    setForm({ title: training.title || "", id_domaine: training.id_domaine || "", id_source: training.id_source || "", location: training.location || "", start_: training.start_ || "", end_: training.end_ || "", duration_hours: training.duration_hours ?? "", cost_hour: training.cost_hour ?? "", mode, id_diploma: training.id_diploma || "", id_certification: training.id_certification || "", skills, original: training });
  }

  function updateField(event) { setForm((current) => ({ ...current, [event.target.name]: event.target.value })); }
  function addSkill() { setForm((current) => ({ ...current, skills: [...current.skills, { id_skill: "", level: 1 }] })); }
  function updateSkill(index, key, value) { setForm((current) => ({ ...current, skills: current.skills.map((item, itemIndex) => itemIndex === index ? { ...item, [key]: value } : item) })); }
  function removeSkill(index) { setForm((current) => ({ ...current, skills: current.skills.filter((_, itemIndex) => itemIndex !== index) })); }

  async function submit(event) {
    event.preventDefault(); if (!form || saving) return;
    const used = Boolean(form.original?.is_used);
    if (!form.title || (!used && (!form.id_domaine || !form.id_source || !form.start_ || !form.end_ || form.duration_hours === "" || form.cost_hour === ""))) { setError("Complétez les champs obligatoires."); return; }
    if (!used && form.start_ > form.end_) { setError("La date de début doit précéder la date de fin."); return; }
    if (!used && form.mode === "skills" && !form.skills.length) { setError("Ajoutez au moins une compétence."); return; }
    if (!used && (new Set(form.skills.map((item) => item.id_skill)).size !== form.skills.length || form.skills.some((item) => !item.id_skill || Number(item.level) < 1))) { setError("Les compétences doivent être uniques et avoir un niveau valide."); return; }
    const payload = { title: form.title, id_domaine: Number(form.id_domaine), id_source: Number(form.id_source), location: form.location || null, start_: form.start_, end_: form.end_, duration_hours: form.duration_hours, cost_hour: form.cost_hour, id_diploma: form.mode === "diploma" ? Number(form.id_diploma) : null, id_certification: form.mode === "certification" ? Number(form.id_certification) : null, skills: form.mode === "skills" ? form.skills.map((item) => ({ id_skill: Number(item.id_skill), level: Number(item.level) })) : [] };
    if ((form.mode === "diploma" && !form.id_diploma) || (form.mode === "certification" && !form.id_certification)) { setError("Sélectionnez le support choisi."); return; }
    setSaving(true); setError("");
    try {
      if (form.original) {
        const updatePayload = form.original.is_used ? { title: form.title, location: form.location || null } : payload;
        await updateTraining(form.original.id_training, updatePayload);
      } else await createTraining(payload);
      setForm(null); setFeedback("La formation a été enregistrée."); await load();
    } catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(errorMessage(requestError, "La formation n'a pas pu être enregistrée.")); }
    finally { setSaving(false); }
  }

  async function archive(training) {
    if (deleting !== null || !window.confirm(`Archiver « ${training.title} » ?`)) return;
    setDeleting(training.id_training); setError("");
    try { await archiveTraining(training.id_training); setFeedback("La formation a été archivée."); await load(); }
    catch (requestError) { setError(errorMessage(requestError, "La formation n'a pas pu être archivée.")); }
    finally { setDeleting(null); }
  }

  if (loading) return <section className="screen-state">Chargement des formations…</section>;
  return <section>
    <div className="page-heading"><div><p className="eyebrow">Administration HR</p><h1>Administration des formations</h1></div><button className="button button-primary" onClick={openCreate}>Nouvelle formation</button></div>
    {error && <p className="page-alert">{error}</p>}{feedback && <p className="form-feedback">{feedback}</p>}
    {form && <form className="training-admin-form" onSubmit={submit}><div className="page-heading"><h2>{form.original ? "Modifier la formation" : "Nouvelle formation"}</h2><button type="button" className="button button-secondary" onClick={() => setForm(null)}>Annuler</button></div>
      <label>Titre<input name="title" value={form.title} onChange={updateField} required /></label>
      <div className="admin-form-grid"><label>Domaine<select name="id_domaine" value={form.id_domaine} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)}><option value="">Sélectionner</option>{refs.domaines.map((item) => <option key={item.id_domaine} value={item.id_domaine}>{item.nom_domaine}</option>)}</select></label><label>Organisme<select name="id_source" value={form.id_source} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)}><option value="">Sélectionner</option>{refs.sources.map((item) => <option key={item.id_source} value={item.id_source}>{item.name_source}</option>)}</select></label><label>Lieu<input name="location" value={form.location} onChange={updateField} /></label><label>Début<input type="date" name="start_" value={form.start_} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)} /></label><label>Fin<input type="date" name="end_" value={form.end_} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)} /></label><label>Durée (h)<input type="number" min="0" step="0.01" name="duration_hours" value={form.duration_hours} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)} /></label><label>Coût horaire<input type="number" min="0" step="0.01" name="cost_hour" value={form.cost_hour} onChange={updateField} required={!form.original?.is_used} disabled={Boolean(form.original?.is_used)} /></label></div>
      {form.original?.is_used && <p className="muted">Cette formation est déjà utilisée. Seuls le titre et le lieu peuvent être modifiés.</p>}
      <label>Mode d’acquisition<select name="mode" value={form.mode} onChange={updateField} disabled={Boolean(form.original?.is_used)}><option value="skills">Compétences</option><option value="diploma">Diplôme</option><option value="certification">Certification</option></select></label>
      {form.mode === "diploma" && <label>Diplôme<select name="id_diploma" value={form.id_diploma} onChange={updateField} required disabled={Boolean(form.original?.is_used)}><option value="">Sélectionner</option>{refs.diplomas.map((item) => <option key={item.id_diploma} value={item.id_diploma}>{item.subject_diploma}</option>)}</select></label>}
      {form.mode === "certification" && <label>Certification<select name="id_certification" value={form.id_certification} onChange={updateField} required disabled={Boolean(form.original?.is_used)}><option value="">Sélectionner</option>{refs.certifications.map((item) => <option key={item.id_certification} value={item.id_certification}>{item.subject_certification}</option>)}</select></label>}
      {form.mode === "skills" && <div className="training-skill-editor"><div className="admin-section-heading"><h3>Compétences accordées</h3><button type="button" className="button button-secondary" onClick={addSkill} disabled={Boolean(form.original?.is_used)}>Ajouter</button></div>{form.skills.map((item, index) => <div className="training-skill-row" key={`${index}-${item.id_skill}`}><select value={item.id_skill} onChange={(event) => updateSkill(index, "id_skill", event.target.value)} disabled={Boolean(form.original?.is_used)}><option value="">Compétence</option>{refs.skills.map((skill) => <option key={skill.id_skill} value={skill.id_skill}>{skill.name_skill}</option>)}</select><input type="number" min="1" step="1" value={item.level} onChange={(event) => updateSkill(index, "level", event.target.value)} disabled={Boolean(form.original?.is_used)} /><button type="button" className="button button-secondary" onClick={() => removeSkill(index)} disabled={Boolean(form.original?.is_used)}>Supprimer</button></div>)}</div>}
      <button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button>
    </form>}
    {!form && <>
      <div className="training-tabs" role="tablist" aria-label="Vues des formations"><button className={`button ${view === "active" ? "button-primary" : "button-secondary"}`} onClick={() => setView("active")} role="tab" aria-selected={view === "active"}>Formations actives ({activeTrainings.length})</button><button className={`button ${view === "history" ? "button-primary" : "button-secondary"}`} onClick={() => setView("history")} role="tab" aria-selected={view === "history"}>Anciennes formations ({historicalTrainings.length})</button></div>
      {view === "active" && activeTrainings.length === 0 && <div className="empty-state"><h2>Aucune formation active</h2><p>Créez une occurrence ou consultez les anciennes formations.</p></div>}
      {view === "history" && historicalTrainings.length === 0 && <div className="empty-state"><h2>Aucune ancienne formation</h2><p>Les formations terminées apparaîtront ici.</p></div>}
      {(view === "active" ? activeTrainings : historicalTrainings).length > 0 && <div className="training-grid">{(view === "active" ? activeTrainings : historicalTrainings).map(({ training, status }) => <article className="training-card" key={training.id_training}><div className="skill-card-header"><div><p className="temporal-badge">{status.label}</p><h2>{valueLabel(training.title)}</h2></div></div><p>{valueLabel(training.domaine_name)} · {valueLabel(training.source_name)}</p><p>{valueLabel(training.location)}</p><p>{dateLabel(training.start_)} → {dateLabel(training.end_)}</p><p>{valueLabel(training.duration_hours)} h · {valueLabel(training.cost_hour)} €/h</p><p><strong>{training.diploma_name ? `Diplôme : ${training.diploma_name}` : training.certification_name ? `Certification : ${training.certification_name}` : "Compétences"}</strong></p>{training.is_used && <p className="muted">Occurrence utilisée</p>}{view === "active" && <div className="request-actions"><button className="button button-secondary" onClick={() => openEdit(training)}>Modifier</button><button className="button button-danger" onClick={() => archive(training)} disabled={deleting === training.id_training}>{deleting === training.id_training ? "Archivage…" : "Archiver"}</button></div>}</article>)}</div>}
    </>}
  </section>;
}
