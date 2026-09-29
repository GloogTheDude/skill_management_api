import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { getEmployeeSkillProfile } from "../api/skills";
import { createSkillValidation, getAllSkills, getSkillValidationHistory, getValidationTypes } from "../api/skills";
import SkillProfileList from "../components/SkillProfileList";
import { useAuth } from "../auth/AuthContext";

export default function EmployeeSkillProfilePage() {
  const { idEmployee } = useParams();
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [referenceData, setReferenceData] = useState({ skills: [], validationTypes: [] });
  const [evaluation, setEvaluation] = useState(null);
  const [history, setHistory] = useState(null);
  const [saving, setSaving] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const canEvaluate = [2, 3].includes(Number(user?.access_level)) && Number(user?.id_employee) !== Number(idEmployee);

  useEffect(() => {
    let cancelled = false;
    async function loadProfile() {
      setLoading(true);
      setError(null);
      try {
        const profile = await getEmployeeSkillProfile(idEmployee);
        if (!cancelled) setSkills(profile);
      } catch (requestError) {
        if (cancelled) return;
        if (requestError instanceof ApiError && requestError.status === 401) {
          await logout().catch(() => undefined);
          navigate("/login", { replace: true });
          return;
        }
        setError(requestError);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadProfile();
    return () => { cancelled = true; };
  }, [idEmployee, logout, navigate]);

  useEffect(() => {
    if (!canEvaluate) return undefined;
    let cancelled = false;
    Promise.all([getAllSkills(), getValidationTypes()]).then(([availableSkills, validationTypes]) => {
      if (!cancelled) setReferenceData({ skills: availableSkills, validationTypes });
    }).catch(() => undefined);
    return () => { cancelled = true; };
  }, [canEvaluate]);

  function openEvaluation(skill) {
    setEvaluation({
      skill,
      idSkill: skill.skill_id,
      level: skill.evaluated_level ?? "",
      idValidation: "",
      justification: "",
    });
    setError(null);
  }

  async function openHistory(skill) {
    setLoadingHistory(true);
    setError(null);
    try {
      setHistory({ skill, items: await getSkillValidationHistory(idEmployee, skill.skill_id) });
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setError(requestError);
    } finally {
      setLoadingHistory(false);
    }
  }

  async function submitEvaluation(event) {
    event.preventDefault();
    if (!evaluation.level || !evaluation.idValidation) return;
    setSaving(true);
    setError(null);
    try {
      await createSkillValidation({
        id_employee: Number(idEmployee),
        id_skill: Number(evaluation.idSkill),
        level_skill: Number(evaluation.level),
        id_validation: Number(evaluation.idValidation),
        ...(evaluation.justification.trim() ? { justification: evaluation.justification.trim() } : {}),
      });
      setEvaluation(null);
      const profile = await getEmployeeSkillProfile(idEmployee);
      setSkills(profile);
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setError(requestError);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="screen-state">Chargement du profil de compétences…</div>;
  if (error) {
    let message = "Impossible de charger ce profil de compétences. Réessayez plus tard.";
    if (error instanceof ApiError && error.status === 403) message = "Vous n’êtes pas autorisé à consulter ce profil.";
    if (error instanceof ApiError && error.status === 404) message = "Cet Employee ou ce profil n’existe pas.";
    return (
      <div>
        <div className="alert page-alert" role="alert">{message}</div>
        {location.state?.returnTo && <button className="button button-secondary" type="button" onClick={() => navigate(location.state.returnTo)}>Retour aux résultats</button>}
      </div>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div><p className="eyebrow">Profil de compétences</p><h1>Profil de compétences</h1></div>
        <span className="skill-count">{skills.length} compétence{skills.length === 1 ? "" : "s"}</span>
      </div>
      {location.state?.returnTo && <button className="button button-secondary profile-back-button" type="button" onClick={() => navigate(location.state.returnTo)}>Retour aux résultats</button>}
      {skills.length === 0 ? (
        <div className="empty-state"><h2>Aucune compétence à afficher</h2><p>Ce profil ne contient pas encore de compétence acquise ou validée.</p></div>
      ) : <SkillProfileList skills={skills} canEvaluate={canEvaluate} onEvaluate={openEvaluation} onHistory={openHistory} />}
      {canEvaluate && <button className="button button-secondary" type="button" onClick={() => openEvaluation({ skill_id: "", skill_name: "", skill_domaine: "", evaluated_level: null })}>Évaluer une nouvelle compétence</button>}

      {evaluation && (
        <div className="modal-backdrop" role="presentation" onClick={() => !saving && setEvaluation(null)}>
          <section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="evaluation-title" onClick={(event) => event.stopPropagation()}>
            <h2 id="evaluation-title">{evaluation.skill.current_validation ? "Réévaluer une compétence" : "Évaluer une compétence"}</h2>
            {evaluation.skill.skill_id ? <p><strong>{evaluation.skill.skill_name}</strong> — {evaluation.skill.skill_domaine || "Domaine non renseigné"}</p> : (
              <label>Compétence
                <select value={evaluation.idSkill} onChange={(event) => setEvaluation({ ...evaluation, idSkill: event.target.value, skill: referenceData.skills.find((item) => item.id_skill === Number(event.target.value)) || evaluation.skill })}>
                  <option value="">Choisir une compétence</option>
                  {referenceData.skills.filter((item) => !skills.some((skill) => skill.skill_id === item.id_skill)).map((skill) => <option key={skill.id_skill} value={skill.id_skill}>{skill.name_skill} — {skill.name_domaine || "Domaine non renseigné"}</option>)}
                </select>
              </label>
            )}
            {evaluation.skill.current_validation && <p>Évaluation actuelle : niveau {evaluation.skill.current_validation.level}</p>}
            <form onSubmit={submitEvaluation}>
              <label>Niveau terrain
                <input required type="number" step="1" value={evaluation.level} onChange={(event) => setEvaluation({ ...evaluation, level: event.target.value })} />
              </label>
              <label>Type de validation
                <select required value={evaluation.idValidation} onChange={(event) => setEvaluation({ ...evaluation, idValidation: event.target.value })}>
                  <option value="">Choisir un type</option>
                  {referenceData.validationTypes.map((type) => <option key={type.id_validation} value={type.id_validation}>{type.denomination_validation || type.source || `Type ${type.id_validation}`}</option>)}
                </select>
              </label>
              <label>Justification
                <textarea maxLength="1000" value={evaluation.justification} onChange={(event) => setEvaluation({ ...evaluation, justification: event.target.value })} />
              </label>
              <div className="card-actions"><button className="button button-secondary" type="button" disabled={saving} onClick={() => setEvaluation(null)}>Annuler</button><button className="button button-primary" type="submit" disabled={saving}>{saving ? "Enregistrement…" : "Enregistrer l’évaluation"}</button></div>
            </form>
          </section>
        </div>
      )}
      {history && <div className="modal-backdrop" role="presentation" onClick={() => setHistory(null)}><section className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="history-title" onClick={(event) => event.stopPropagation()}><h2 id="history-title">Historique — {history.skill.skill_name}</h2>{history.items.map((item) => <article className="history-item" key={item.id_skill_validation}><strong>Niveau {item.level_skill}</strong><span>{item.validated_at ? new Intl.DateTimeFormat("fr-BE").format(new Date(item.validated_at)) : "Date inconnue"}</span><span>{[item.validator_first_name, item.validator_last_name].filter(Boolean).join(" ") || `Validator #${item.id_validator}`}</span><span>{item.validation_type_name || `Type #${item.id_validation}`}</span><span>{item.superseded_at ? "Superseded" : "Current"}</span><p>{item.justification || "Aucune justification"}</p></article>)}<button className="button button-secondary" type="button" onClick={() => setHistory(null)}>Fermer</button></section></div>}
      {loadingHistory && <p className="screen-state">Chargement de l’historique…</p>}
    </section>
  );
}
