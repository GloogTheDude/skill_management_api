import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import {
  archiveCertification, archiveDiploma, archiveDomaine, archiveSkill, archiveTrainingSource, archiveValidationType,
  createCertification, createDiploma, createDomaine, createSkill, createTrainingSource, createValidationType,
  getCertifications, getCertificationSkills, getDiplomas, getDiplomaSkills, getDomaines, getSkills, getTrainingSources, getValidationTypes,
  getRoles, getAccessLevels, createRole, updateRole, archiveRole, createAccessLevel, updateAccessLevel, archiveAccessLevel,
  replaceCertificationSkills, replaceDiplomaSkills, updateCertification, updateDiploma, updateDomaine, updateSkill, updateTrainingSource, updateValidationType,
} from "../api/references";

const tabs = [
  ["domains", "Domaines"], ["sources", "Sources"], ["skills", "Compétences"],
  ["diplomas", "Diplômes"], ["certifications", "Certifications"], ["validation-types", "Types de validation"],
  ["roles", "Rôles"], ["access-levels", "Niveaux d’accès"],
];

const configs = {
  domains: { collection: "domains", title: "Domaines", singular: "Domaine", name: "nom_domaine", create: createDomaine, update: updateDomaine, archive: archiveDomaine, columns: (item) => [item.nom_domaine] },
  sources: { collection: "sources", title: "Sources de formation", singular: "Source", name: "name_source", create: createTrainingSource, update: updateTrainingSource, archive: archiveTrainingSource, columns: (item) => [item.name_source] },
  skills: { collection: "skills", title: "Compétences", singular: "Compétence", name: "name_skill", create: createSkill, update: updateSkill, archive: archiveSkill, columns: (item) => [item.name_skill, item.name_domaine || "Domaine non renseigné"] },
  diplomas: { collection: "diplomas", title: "Diplômes", singular: "Diplôme", name: "subject_diploma", create: createDiploma, update: updateDiploma, archive: archiveDiploma, columns: (item) => [item.subject_diploma, item.domaine_name || "Domaine non renseigné"] },
  certifications: { collection: "certifications", title: "Certifications", singular: "Certification", name: "subject_certification", create: createCertification, update: updateCertification, archive: archiveCertification, columns: (item) => [item.subject_certification, item.domaine_name || "Domaine non renseigné", item.validity_month ? `${item.validity_month} mois` : "Durée non renseignée"] },
  "validation-types": { collection: "validationTypes", title: "Types de validation", singular: "Type de validation", name: "denomination_validation", create: createValidationType, update: updateValidationType, archive: archiveValidationType, columns: (item) => [item.denomination_validation || "Sans dénomination", item.source || "Source non renseignée"] },
  roles: { collection: "roles", title: "Rôles", singular: "Rôle", name: "denomination_role", create: createRole, update: updateRole, archive: archiveRole, columns: (item) => [item.denomination_role || "Sans dénomination", item.access_level_label || "Niveau non renseigné"] },
  "access-levels": { collection: "accessLevels", title: "Niveaux d’accès", singular: "Niveau d’accès", name: "label", create: createAccessLevel, update: updateAccessLevel, archive: archiveAccessLevel, columns: (item) => [item.label, `Rang ${item.level}`, item.permission_profile] },
};

function errorMessage(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 401) return "Votre session a expiré.";
  if (error.status === 403) return "Vous n’êtes pas autorisé à administrer les référentiels.";
  if ([409, 422].includes(error.status) && error.detail) return error.detail;
  if (error.status === 404) return "La ressource demandée n’existe plus.";
  return fallback;
}

function blankFor(type) {
  if (type === "domains") return { nom_domaine: "" };
  if (type === "sources") return { name_source: "" };
  if (type === "skills") return { name_skill: "", id_domaine: "" };
  if (type === "diplomas") return { subject_diploma: "", level_diploma: "", id_domaine: "" };
  if (type === "certifications") return { subject_certification: "", validity_month: "", id_domaine: "" };
  if (type === "roles") return { denomination_role: "", id_access_level: "" };
  if (type === "access-levels") return { label: "", level: "", permission_profile: "EMPLOYEE" };
  return { denomination_validation: "", source: "" };
}

export default function ReferenceAdminPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedType = searchParams.get("type");
  const type = configs[requestedType] ? requestedType : "domains";
  const config = configs[type];
  const [data, setData] = useState({ domains: [], sources: [], skills: [], diplomas: [], certifications: [], validationTypes: [], roles: [], accessLevels: [], diplomaSkills: [], certificationSkills: [] });
  const [form, setForm] = useState(null);
  const [relations, setRelations] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const loadGeneration = useRef(0);

  const load = useCallback(async () => {
    const generation = ++loadGeneration.current;
    setLoading(true); setError("");
    try {
      const [domains, sources, skills, diplomas, certifications, validationTypes, roles, accessLevels, diplomaSkills, certificationSkills] = await Promise.all([
        getDomaines(), getTrainingSources(), getSkills(), getDiplomas(), getCertifications(), getValidationTypes(), getRoles(), getAccessLevels(), getDiplomaSkills(), getCertificationSkills(),
      ]);
      if (generation !== loadGeneration.current) return;
      setData({ domains, sources, skills, diplomas, certifications, validationTypes, roles, accessLevels, diplomaSkills, certificationSkills });
    } catch (requestError) {
      if (generation !== loadGeneration.current) return;
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(errorMessage(requestError, "Les référentiels n’ont pas pu être chargés."));
    } finally {
      if (generation === loadGeneration.current) setLoading(false);
    }
  }, [logout, navigate]);

  useEffect(() => { if (user?.permission_profile === "HR") load(); else setLoading(false); }, [load, user]);
  useEffect(() => () => { loadGeneration.current += 1; }, []);
  useEffect(() => { if (!configs[requestedType]) setSearchParams({ type: "domains" }, { replace: true }); }, [requestedType, setSearchParams]);

  const visibleItems = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return data[config.collection].filter((item) => !needle || config.columns(item).join(" ").toLowerCase().includes(needle));
  }, [config, data, query]);

  function openCreate() { setError(""); setFeedback(""); setRelations([]); setForm({ mode: "create", id: null, values: blankFor(type) }); }
  function openEdit(item) {
    setError(""); setFeedback("");
    const values = Object.fromEntries(Object.keys(blankFor(type)).map((key) => [key, item[key] ?? ""]));
    const id = item.id_domaine || item.id_source || item.id_skill || item.id_diploma || item.id_certification || item.id_validation || item.id_role || item.id_access_level;
    const links = type === "diplomas" ? data.diplomaSkills.filter((link) => link.id_diploma === id).map((link) => ({ id_skill: link.id_skill, level: link.min_level ?? "" })) : type === "certifications" ? data.certificationSkills.filter((link) => link.id_certification === id).map((link) => ({ id_skill: link.id_skill, level: link.granted_level ?? "" })) : [];
    setRelations(links); setForm({ mode: "edit", id, values });
  }

  async function save(event) {
    event.preventDefault(); setSaving(true); setError(""); setFeedback("");
    let aggregateSaved = false;
    try {
      const values = { ...form.values };
      if (type === "skills" || type === "diplomas" || type === "certifications") values.id_domaine = Number(values.id_domaine);
      if (type === "certifications" && values.validity_month !== "") values.validity_month = Number(values.validity_month);
      if (type === "roles") values.id_access_level = Number(values.id_access_level);
      if (type === "access-levels") values.level = Number(values.level);
      const result = form.mode === "create" ? await config.create(values) : await config.update(form.id, values);
      aggregateSaved = true;
      const id = form.mode === "create" ? (result.id_diploma || result.id_certification) : form.id;
      if (form.mode === "edit" && type === "diplomas") await replaceDiplomaSkills(id, relations.map((item) => ({ id_skill: Number(item.id_skill), level: item.level === "" ? null : Number(item.level) })));
      if (form.mode === "edit" && type === "certifications") await replaceCertificationSkills(id, relations.map((item) => ({ id_skill: Number(item.id_skill), level: item.level === "" ? null : Number(item.level) })));
      setForm(null); setFeedback(`${config.singular} enregistré.`); await load();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      if (aggregateSaved) { setForm(null); await load(); }
      setError(errorMessage(requestError, `${config.singular} non enregistré.`));
    } finally { setSaving(false); }
  }

  async function archive(item) {
    const id = item.id_domaine || item.id_source || item.id_skill || item.id_diploma || item.id_certification || item.id_validation || item.id_role || item.id_access_level;
    if (!window.confirm(`Archiver ${config.singular.toLowerCase()} « ${config.columns(item)[0]} » ?`)) return;
    try { await config.archive(id); setFeedback(`${config.singular} archivé.`); await load(); }
    catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(errorMessage(requestError, `${config.singular} non archivé.`));
    }
  }

  if (user?.permission_profile !== "HR") return <div className="alert page-alert" role="alert">Vous n’êtes pas autorisé à administrer les référentiels.</div>;
  if (loading) return <div className="screen-state">Chargement des référentiels…</div>;
  if (form && (type === "roles" || type === "access-levels")) return <section><div className="page-heading"><h1>{form.mode === "create" ? "Ajouter" : "Modifier"} — {config.singular}</h1></div><form className="modal-panel" onSubmit={save}>{type === "roles" ? <><label>Fonction<input required value={form.values.denomination_role} onChange={(event) => setForm({ ...form, values: { ...form.values, denomination_role: event.target.value } })} /></label><label>AccessLevel<select required value={form.values.id_access_level} onChange={(event) => setForm({ ...form, values: { ...form.values, id_access_level: event.target.value } })}><option value="">Sélectionner</option>{data.accessLevels.map((item) => <option key={item.id_access_level} value={item.id_access_level}>{item.label} — {item.permission_profile}</option>)}</select></label></> : <><label>Libellé<input required value={form.values.label} onChange={(event) => setForm({ ...form, values: { ...form.values, label: event.target.value } })} /></label><label>Rang<input required type="number" value={form.values.level} onChange={(event) => setForm({ ...form, values: { ...form.values, level: event.target.value } })} /></label><label>Profil d’autorisation<select required value={form.values.permission_profile} onChange={(event) => setForm({ ...form, values: { ...form.values, permission_profile: event.target.value } })}><option value="EMPLOYEE">EMPLOYEE</option><option value="MANAGER">MANAGER</option><option value="HR">HR</option></select></label></>}<div className="card-actions"><button className="button button-secondary" type="button" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section>;

  return <section>
    <div className="page-heading"><div><p className="eyebrow">Administration HR</p><h1>Référentiels</h1></div></div>
    {error && <div className="alert page-alert" role="alert">{error}</div>}
    {feedback && <div className="feedback">{feedback}</div>}
    <nav className="reference-tabs" aria-label="Référentiels">{tabs.map(([key, label]) => <button key={key} className={`button ${type === key ? "button-primary" : "button-secondary"}`} type="button" onClick={() => { setSearchParams({ type: key }); setQuery(""); setForm(null); }}>{label}</button>)}</nav>
    <div className="reference-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher…" /><button className="button button-primary" type="button" onClick={openCreate}>Ajouter</button></div>
    {visibleItems.length === 0 ? <div className="empty-state"><h2>Aucun élément</h2><p>{query ? "Aucun résultat pour cette recherche." : "Ce référentiel est vide."}</p></div> : <div className="reference-list" key={type}>{visibleItems.map((item) => { const id = item.id_domaine || item.id_source || item.id_skill || item.id_diploma || item.id_certification || item.id_validation || item.id_role || item.id_access_level; return <article className="reference-card" key={`${type}-${id}`}><div>{config.columns(item).map((column, index) => <p key={index} className={index === 0 ? "reference-primary" : ""}>{column}</p>)}</div><div className="card-actions"><button className="button button-secondary" type="button" onClick={() => openEdit(item)}>Modifier</button><button className="button button-danger" type="button" onClick={() => archive(item)}>Archiver</button></div></article>; })}</div>}
    {form && <div className="modal-backdrop" key={type} role="presentation" onClick={() => !saving && setForm(null)}><section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="reference-form-title" onClick={(event) => event.stopPropagation()}><h2 id="reference-form-title">{form.mode === "create" ? "Ajouter" : "Modifier"} — {config.singular}</h2><form onSubmit={save}>{type === "domains" && <label>Nom<input required maxLength="100" value={form.values.nom_domaine} onChange={(event) => setForm({ ...form, values: { ...form.values, nom_domaine: event.target.value } })} /></label>}{type === "sources" && <label>Nom<input required maxLength="100" value={form.values.name_source} onChange={(event) => setForm({ ...form, values: { ...form.values, name_source: event.target.value } })} /></label>}{type === "skills" && <><label>Nom<input required maxLength="100" value={form.values.name_skill} onChange={(event) => setForm({ ...form, values: { ...form.values, name_skill: event.target.value } })} /></label><DomainSelect values={form.values} data={data} setForm={setForm} form={form} /></>}{(type === "diplomas" || type === "certifications") && <><label>{type === "diplomas" ? "Sujet" : "Sujet de certification"}<input required value={form.values[type === "diplomas" ? "subject_diploma" : "subject_certification"]} onChange={(event) => setForm({ ...form, values: { ...form.values, [type === "diplomas" ? "subject_diploma" : "subject_certification"]: event.target.value } })} /></label>{type === "diplomas" && <label>Niveau du diplôme<input required value={form.values.level_diploma} onChange={(event) => setForm({ ...form, values: { ...form.values, level_diploma: event.target.value } })} /></label>}{type === "certifications" && <label>Validité (mois)<input type="number" min="1" value={form.values.validity_month} onChange={(event) => setForm({ ...form, values: { ...form.values, validity_month: event.target.value } })} /></label>}<DomainSelect values={form.values} data={data} setForm={setForm} form={form} /></>}{type === "validation-types" && <><label>Dénomination<input value={form.values.denomination_validation} onChange={(event) => setForm({ ...form, values: { ...form.values, denomination_validation: event.target.value } })} /></label><label>Source<input value={form.values.source} onChange={(event) => setForm({ ...form, values: { ...form.values, source: event.target.value } })} /></label></>}{(type === "diplomas" || type === "certifications") && form.mode === "edit" && <RelationEditor type={type} relations={relations} setRelations={setRelations} skills={data.skills} /> }<div className="card-actions"><button className="button button-secondary" type="button" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section></div>}
  </section>;
}

function DomainSelect({ values, setForm, form, data }) { return <label>Domaine<select required value={values.id_domaine} onChange={(event) => setForm({ ...form, values: { ...values, id_domaine: event.target.value } })}><option value="">Sélectionner</option>{data.domains.map((item) => <option key={item.id_domaine} value={item.id_domaine}>{item.nom_domaine}</option>)}</select></label>; }

function RelationEditor({ type, relations, setRelations, skills }) { return <div className="relation-editor"><h3>Compétences associées</h3>{relations.map((relation, index) => <div className="relation-row" key={index}><select value={relation.id_skill} onChange={(event) => setRelations(relations.map((item, i) => i === index ? { ...item, id_skill: event.target.value } : item))}><option value="">Compétence</option>{skills.map((skill) => <option key={skill.id_skill} value={skill.id_skill}>{skill.name_skill}</option>)}</select><input type="number" min="1" max="5" value={relation.level} onChange={(event) => setRelations(relations.map((item, i) => i === index ? { ...item, level: event.target.value } : item))} placeholder={type === "diplomas" ? "Niveau min." : "Niveau"} /><button className="button button-secondary" type="button" onClick={() => setRelations(relations.filter((_, i) => i !== index))}>Retirer</button></div>)}<button className="button button-secondary" type="button" onClick={() => setRelations([...relations, { id_skill: "", level: "" }])}>Ajouter une compétence</button></div>; }
