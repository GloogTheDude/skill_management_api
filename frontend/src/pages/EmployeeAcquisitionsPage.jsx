import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { archiveEmployeeCertification, archiveEmployeeDiploma, createEmployeeCertification, createEmployeeDiploma, getEmployee, getEmployeeCertifications, getEmployeeDiplomas, updateEmployeeCertification, updateEmployeeDiploma } from "../api/employees";
import { getCertifications, getDiplomas } from "../api/references";

function message(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 403) return "Vous n’êtes pas autorisé à consulter ou gérer ces acquis.";
  if ([404, 409, 422].includes(error.status) && error.detail) return error.detail;
  return fallback;
}

const emptyDiploma = { id_diploma: "", start_: "", end_: "", school: "", distinction: "", doc: "" };
const emptyCertification = { id_certification: "", start_: "", end_: "", expiration: "", organism: "", evaluation: "", doc: "" };

export default function EmployeeAcquisitionsPage() {
  const { idEmployee } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [diplomas, setDiplomas] = useState([]); const [certifications, setCertifications] = useState([]);
  const [diplomaRefs, setDiplomaRefs] = useState([]); const [certificationRefs, setCertificationRefs] = useState([]);
  const [employee, setEmployee] = useState(null); const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true); const [saving, setSaving] = useState(false); const [error, setError] = useState("");
  const canRead = ["MANAGER", "HR"].includes(user?.permission_profile); const canAdminister = user?.permission_profile === "HR";
  const tab = searchParams.get("type") === "certifications" ? "certifications" : "diplomas";

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [employeeData, diplomaData, certificationData, diplomaDataRefs, certificationDataRefs] = await Promise.all([
        getEmployee(idEmployee), getEmployeeDiplomas(idEmployee), getEmployeeCertifications(idEmployee),
        canAdminister ? getDiplomas() : Promise.resolve([]), canAdminister ? getCertifications() : Promise.resolve([]),
      ]);
      setEmployee(employeeData); setDiplomas(diplomaData); setCertifications(certificationData); setDiplomaRefs(diplomaDataRefs); setCertificationRefs(certificationDataRefs);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(message(requestError, "Les acquis n’ont pas pu être chargés."));
    } finally { setLoading(false); }
  }, [canAdminister, idEmployee, logout, navigate]);

  useEffect(() => { if (canRead) load(); else setLoading(false); }, [canRead, load]);
  function openCreate(type) { if (!canAdminister) return; setError(""); setForm({ type, id: null, values: type === "diplomas" ? { ...emptyDiploma } : { ...emptyCertification } }); }
  function openEdit(type, item) { if (!canAdminister) return; const empty = type === "diplomas" ? emptyDiploma : emptyCertification; setForm({ type, id: type === "diplomas" ? item.id_diploma : item.id_employee_certification, values: Object.fromEntries(Object.keys(empty).map((key) => [key, item[key] ?? ""])) }); }
  function setValue(name, value) { setForm((current) => ({ ...current, values: { ...current.values, [name]: value } })); }
  async function save(event) {
    event.preventDefault(); if (!canAdminister || saving) return; setSaving(true); setError("");
    try {
      const values = { ...form.values, id_employee: Number(idEmployee) };
      if (form.type === "diplomas") { values.id_diploma = Number(values.id_diploma); form.id === null ? await createEmployeeDiploma(values) : await updateEmployeeDiploma(idEmployee, form.id, values); }
      else { values.id_certification = Number(values.id_certification); form.id === null ? await createEmployeeCertification(values) : await updateEmployeeCertification(form.id, values); }
      setForm(null); await load();
    } catch (requestError) { if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; } setError(message(requestError, "L’acquis n’a pas pu être enregistré.")); }
    finally { setSaving(false); }
  }
  async function archive(type, item) {
    if (!canAdminister || !window.confirm("Archiver cet acquis ?")) return;
    try { if (type === "diplomas") await archiveEmployeeDiploma(idEmployee, item.id_diploma); else await archiveEmployeeCertification(item.id_employee_certification); await load(); }
    catch (requestError) { setError(message(requestError, "L’acquis n’a pas pu être archivé.")); }
  }

  if (!canRead) return <div className="alert page-alert">Vous n’êtes pas autorisé à consulter les acquis de cet Employee.</div>;
  if (loading) return <div className="screen-state">Chargement des acquis…</div>;
  const employeeName = employee ? `${employee.first_name || ""} ${employee.last_name || ""}`.trim() : `#${idEmployee}`;
  const items = tab === "diplomas" ? diplomas : certifications; const refs = tab === "diplomas" ? diplomaRefs : certificationRefs;
  return <section>
    <div className="page-heading"><div><p className="eyebrow">{canAdminister ? "Administration HR" : "Consultation"}</p><h1>Acquis de l’Employee {employeeName}</h1></div><Link className="button button-secondary" to={canAdminister ? "/app/employees" : "/app/team"}>Retour</Link></div>
    {error && <div className="alert page-alert">{error}</div>}
    <nav className="reference-tabs"><button className={`button ${tab === "diplomas" ? "button-primary" : "button-secondary"}`} onClick={() => setSearchParams({ type: "diplomas" })}>Diplômes</button><button className={`button ${tab === "certifications" ? "button-primary" : "button-secondary"}`} onClick={() => setSearchParams({ type: "certifications" })}>Certifications</button></nav>
    <div className="page-heading"><h2>{tab === "diplomas" ? "Diplômes détenus" : "Certifications détenues"}</h2>{canAdminister && <button className="button button-primary" onClick={() => openCreate(tab)}>Ajouter</button>}</div>
    {items.length === 0 ? <div className="empty-state"><h2>Aucun acquis</h2><p>{canAdminister ? "Ajoutez un acquis externe ou historique." : "Aucun acquis enregistré."}</p></div> : <div className="reference-list">{items.map((item) => <article className="reference-card" key={tab === "diplomas" ? item.id_diploma : item.id_employee_certification}><div><p className="reference-primary">{tab === "diplomas" ? item.diploma_name || `Diplôme #${item.id_diploma}` : item.certification_name || `Certification #${item.id_certification}`}</p><p>{item.start_ || "Date de début non renseignée"} → {item.end_ || "Date de fin non renseignée"}</p>{tab === "certifications" && <p>Expiration : {item.expiration || "Non renseignée"}</p>}</div>{canAdminister && <div className="card-actions"><button className="button button-secondary" onClick={() => openEdit(tab, item)}>Modifier</button><button className="button button-danger" onClick={() => archive(tab, item)}>Archiver</button></div>}</article>)}</div>}
    {form && canAdminister && <div className="modal-backdrop"><section className="modal-panel"><h2>{form.id === null ? "Ajouter" : "Modifier"} — {tab === "diplomas" ? "Diplôme" : "Certification"}</h2><form onSubmit={save}><label>{tab === "diplomas" ? "Diplôme" : "Certification"}<select required disabled={form.id !== null} value={form.values[tab === "diplomas" ? "id_diploma" : "id_certification"]} onChange={(event) => setValue(tab === "diplomas" ? "id_diploma" : "id_certification", event.target.value)}><option value="">Sélectionner</option>{refs.map((item) => <option key={item[tab === "diplomas" ? "id_diploma" : "id_certification"]} value={item[tab === "diplomas" ? "id_diploma" : "id_certification"]}>{tab === "diplomas" ? item.subject_diploma : item.subject_certification}</option>)}</select></label><label>Début<input type="date" value={form.values.start_} onChange={(event) => setValue("start_", event.target.value)} /></label><label>Fin<input type="date" value={form.values.end_} onChange={(event) => setValue("end_", event.target.value)} /></label>{tab === "certifications" && <label>Expiration<input type="date" value={form.values.expiration} onChange={(event) => setValue("expiration", event.target.value)} /></label>}<label>{tab === "diplomas" ? "École" : "Organisme"}<input value={form.values[tab === "diplomas" ? "school" : "organism"]} onChange={(event) => setValue(tab === "diplomas" ? "school" : "organism", event.target.value)} /></label>{tab === "diplomas" ? <><label>Distinction<input value={form.values.distinction} onChange={(event) => setValue("distinction", event.target.value)} /></label><label>Document (référence)<input value={form.values.doc} onChange={(event) => setValue("doc", event.target.value)} /></label></> : <><label>Évaluation<input value={form.values.evaluation} onChange={(event) => setValue("evaluation", event.target.value)} /></label><label>Document (référence)<input value={form.values.doc} onChange={(event) => setValue("doc", event.target.value)} /></label></>}<div className="card-actions"><button type="button" className="button button-secondary" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section></div>}
  </section>;
}
