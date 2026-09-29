import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { archiveEmployee, createEmployee, getEmployees, getRoles, updateEmployee } from "../api/employees";
import { useAuth } from "../auth/AuthContext";

function message(error, fallback) {
  if (!(error instanceof ApiError)) return fallback;
  if (error.status === 403) return "Vous n’êtes pas autorisé à administrer les Employees.";
  if ([404, 409, 422].includes(error.status) && error.detail) return error.detail;
  return fallback;
}

export default function EmployeeAdminPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [roles, setRoles] = useState([]);
  const [query, setQuery] = useState("");
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [employeeData, roleData] = await Promise.all([getEmployees(), getRoles()]);
      setEmployees(employeeData); setRoles(roleData);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(message(requestError, "Impossible de charger les Employees."));
    } finally { setLoading(false); }
  }, [logout, navigate]);

  useEffect(() => { if (user?.access_level === 3) load(); else setLoading(false); }, [load, user]);

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return employees.filter((employee) => !needle || [employee.first_name, employee.last_name, employee.mail, employee.denomination_role, employee.manager_name].filter(Boolean).join(" ").toLowerCase().includes(needle));
  }, [employees, query]);

  function openCreate() { setError(""); setFeedback(""); setForm({ mode: "create", id: null, values: { first_name: "", last_name: "", mail: "", password: "", id_role: "", id_manager: "" } }); }
  function openEdit(employee) { setError(""); setFeedback(""); setForm({ mode: "edit", id: employee.id_employee, values: { first_name: employee.first_name || "", last_name: employee.last_name || "", mail: employee.mail || "", password: "", id_role: employee.id_role, id_manager: employee.id_manager || "" } }); }
  function setValue(name, value) { setForm((current) => ({ ...current, values: { ...current.values, [name]: value } })); }

  async function save(event) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const values = { ...form.values, id_role: Number(form.values.id_role), id_manager: form.values.id_manager ? Number(form.values.id_manager) : null };
      if (form.mode === "edit" && !values.password) delete values.password;
      form.mode === "create" ? await createEmployee(values) : await updateEmployee(form.id, values);
      setForm(null); setFeedback("Employee enregistré."); await load();
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) { await logout().catch(() => undefined); navigate("/login", { replace: true }); return; }
      setError(message(requestError, "L’Employee n’a pas pu être enregistré."));
    } finally { setSaving(false); }
  }

  async function archive(employee) {
    if (!window.confirm(`Archiver ${employee.first_name || ""} ${employee.last_name || ""} ?`)) return;
    try { await archiveEmployee(employee.id_employee); setFeedback("Employee archivé."); await load(); }
    catch (requestError) { setError(message(requestError, "L’Employee n’a pas pu être archivé.")); }
  }

  if (user?.access_level !== 3) return <div className="alert page-alert" role="alert">Vous n’êtes pas autorisé à administrer les Employees.</div>;
  if (loading) return <div className="screen-state">Chargement des Employees…</div>;
  return <section>
    <div className="page-heading"><div><p className="eyebrow">Administration HR</p><h1>Employees</h1></div><button className="button button-primary" type="button" onClick={openCreate}>Nouvel Employee</button></div>
    {error && <div className="alert page-alert" role="alert">{error}</div>}{feedback && <p className="form-feedback" role="status">{feedback}</p>}
    <div className="reference-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rechercher un nom, un rôle…" /></div>
    {visible.length === 0 ? <div className="empty-state"><h2>Aucun Employee</h2><p>{query ? "Aucun résultat pour cette recherche." : "La liste est vide."}</p></div> : <div className="reference-list">{visible.map((employee) => <article className="reference-card" key={employee.id_employee}><div><p className="reference-primary">{employee.first_name} {employee.last_name}</p><p>{employee.mail || "Email non renseigné"}</p><p>{employee.denomination_role || "Rôle non renseigné"} · {employee.access_level_label || "AccessLevel non renseigné"}</p><p>Manager : {employee.manager_name || "Aucun"}</p></div><div className="card-actions"><button className="button button-secondary" type="button" onClick={() => openEdit(employee)}>Modifier</button><button className="button button-danger" type="button" onClick={() => archive(employee)}>Archiver</button></div></article>)}</div>}
    {form && <div className="modal-backdrop" role="presentation" onClick={() => !saving && setForm(null)}><section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="employee-form-title" onClick={(event) => event.stopPropagation()}><h2 id="employee-form-title">{form.mode === "create" ? "Nouvel Employee" : "Modifier Employee"}</h2><form onSubmit={save}><label>Prénom<input maxLength="50" value={form.values.first_name} onChange={(event) => setValue("first_name", event.target.value)} /></label><label>Nom<input maxLength="50" value={form.values.last_name} onChange={(event) => setValue("last_name", event.target.value)} /></label><label>Email<input type="email" maxLength="50" value={form.values.mail} onChange={(event) => setValue("mail", event.target.value)} /></label><label>{form.mode === "create" ? "Mot de passe" : "Nouveau mot de passe"}<input type="password" required={form.mode === "create"} value={form.values.password} onChange={(event) => setValue("password", event.target.value)} /></label><label>Rôle<select required value={form.values.id_role} onChange={(event) => setValue("id_role", event.target.value)}><option value="">Sélectionner</option>{roles.map((role) => <option key={role.id_role} value={role.id_role}>{role.denomination_role || `Rôle ${role.id_role}`} — {role.access_level_label}</option>)}</select></label><label>Manager<select value={form.values.id_manager} onChange={(event) => setValue("id_manager", event.target.value)}><option value="">Aucun</option>{employees.filter((employee) => employee.id_employee !== form.id).map((employee) => <option key={employee.id_employee} value={employee.id_employee}>{employee.first_name} {employee.last_name}</option>)}</select></label><div className="card-actions"><button className="button button-secondary" type="button" disabled={saving} onClick={() => setForm(null)}>Annuler</button><button className="button button-primary" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer"}</button></div></form></section></div>}
  </section>;
}
