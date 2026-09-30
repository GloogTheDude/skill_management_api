import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { searchEmployeesBySkills } from "../api/employeeSearch";
import { getAllSkills } from "../api/skills";
import { useAuth } from "../auth/AuthContext";

function emptyRequirement() {
  return { id_skill: "", operator: "gte", level: "1" };
}

function sourceLabel(source) {
  return `${source.source_type} · niveau ${source.level ?? "non renseigné"}`;
}

function parseCriteria(params, skills) {
  const skillIds = params.getAll("skill");
  const operators = params.getAll("operator");
  const levels = params.getAll("level");
  if (!skillIds.length || skillIds.length !== operators.length || skillIds.length !== levels.length) return null;
  const knownSkills = new Set(skills.map((skill) => skill.id_skill));
  const parsed = skillIds.map((skillId, index) => ({ id_skill: skillId, operator: operators[index], level: levels[index] }));
  if (parsed.some((criterion) => (
    !/^\d+$/.test(criterion.id_skill)
    || !knownSkills.has(Number(criterion.id_skill))
    || !["gte", "lte"].includes(criterion.operator)
    || !/^[1-5]$/.test(criterion.level)
  ))) return null;
  return parsed;
}

export default function EmployeeSkillSearchPage() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [skills, setSkills] = useState([]);
  const [requirements, setRequirements] = useState([emptyRequirement()]);
  const [results, setResults] = useState(null);
  const [loadingSkills, setLoadingSkills] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadSkills() {
      try {
        setSkills(await getAllSkills());
      } catch (requestError) {
        if (requestError instanceof ApiError && requestError.status === 401) {
          await logout().catch(() => undefined);
          navigate("/login", { replace: true });
          return;
        }
        setError(requestError);
      } finally {
        setLoadingSkills(false);
      }
    }
    loadSkills();
  }, [logout, navigate]);

  useEffect(() => {
    if (loadingSkills) return undefined;
    const parsed = parseCriteria(searchParams, skills);
    if (!parsed) {
      if ([...searchParams.keys()].length > 0) setSearchParams({}, { replace: true });
      setRequirements([emptyRequirement()]);
      setResults(null);
      return undefined;
    }

    let cancelled = false;
    setRequirements(parsed);
    setSearching(true);
    setError(null);
    searchEmployeesBySkills(parsed.map((criterion) => ({
      id_skill: Number(criterion.id_skill),
      operator: criterion.operator,
      level: Number(criterion.level),
    }))).then((response) => {
      if (!cancelled) setResults(response);
    }).catch(async (requestError) => {
      if (cancelled) return;
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setError(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à effectuer cette recherche."
        : "La recherche n’a pas pu être effectuée. Réessayez plus tard.");
      setResults(null);
    }).finally(() => {
      if (!cancelled) setSearching(false);
    });
    return () => { cancelled = true; };
  }, [loadingSkills, skills, searchParams, setSearchParams, logout, navigate]);

  function updateRequirement(index, field, value) {
    setRequirements((current) => current.map((requirement, requirementIndex) => (
      requirementIndex === index ? { ...requirement, [field]: value } : requirement
    )));
  }

  function addRequirement() {
    setRequirements((current) => [...current, emptyRequirement()]);
  }

  function removeRequirement(index) {
    setRequirements((current) => current.filter((_, requirementIndex) => requirementIndex !== index));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (requirements.length === 0 || requirements.some((requirement) => !requirement.id_skill)) {
      setError("Sélectionnez une compétence pour chaque critère.");
      return;
    }
    const params = new window.URLSearchParams();
    requirements.forEach((requirement) => {
      params.append("skill", requirement.id_skill);
      params.append("operator", requirement.operator);
      params.append("level", requirement.level);
    });
    setSearchParams(params);
  }

  if (loadingSkills) return <div className="screen-state">Chargement des compétences…</div>;

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">Manager / HR</p>
          <h1>Recherche employés</h1>
        </div>
      </div>
      {error && <div className="alert page-alert" role="alert">{error}</div>}
      <form className="search-form" onSubmit={handleSubmit}>
        <p className="muted">Tous les critères doivent être satisfaits.</p>
        {requirements.map((requirement, index) => (
          <div className="search-row" key={`requirement-${index}`}>
            <label>
              Compétence
              <select value={requirement.id_skill} onChange={(event) => updateRequirement(index, "id_skill", event.target.value)}>
                <option value="">Choisir une compétence</option>
                {skills.map((skill) => <option key={skill.id_skill} value={skill.id_skill}>{skill.name_skill}</option>)}
              </select>
            </label>
            <label>
              Comparaison
              <select value={requirement.operator} onChange={(event) => updateRequirement(index, "operator", event.target.value)}>
                <option value="gte">Au moins</option>
                <option value="lte">Au plus</option>
              </select>
            </label>
            <label>
              Niveau
              <select value={requirement.level} onChange={(event) => updateRequirement(index, "level", event.target.value)}>
                {[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level}</option>)}
              </select>
            </label>
            {requirements.length > 1 && <button className="button button-secondary" type="button" onClick={() => removeRequirement(index)}>Retirer</button>}
          </div>
        ))}
        <div className="search-actions">
          <button className="button button-secondary" type="button" onClick={addRequirement}>Ajouter une compétence</button>
          <button className="button button-primary" type="submit" disabled={searching}>{searching ? "Recherche…" : "Rechercher"}</button>
        </div>
      </form>
      {results === null ? (
        <div className="empty-state"><h2>Lancez une recherche</h2><p>Les résultats apparaîtront ici.</p></div>
      ) : results.length === 0 ? (
        <div className="empty-state"><h2>Aucun Employee trouvé</h2><p>Aucun Employee ne correspond à tous les critères.</p></div>
      ) : (
        <div className="employee-search-results">
          {results.map((employee) => (
            <article className="request-card" key={employee.id_employee}>
              <h2>{employee.first_name} {employee.last_name}</h2>
              {employee.skills.filter((skill) => requirements.some((requirement) => Number(requirement.id_skill) === skill.skill_id)).map((skill) => (
                <div className="search-result-skill" key={skill.skill_id}>
                  <strong>{skill.skill_name}</strong>
                  <span>Acquis : {skill.acquired_level ?? "non renseigné"} · Évalué : {skill.evaluated_level ?? "non évalué"}</span>
                  {skill.sources.length > 0 && <ul className="skill-sources">{skill.sources.map((source) => <li key={`${source.source_type}-${source.source_id}`}>{sourceLabel(source)}</li>)}</ul>}
                </div>
              ))}
              <button
                className="button button-secondary"
                type="button"
                onClick={() => navigate(`/app/employees/${employee.id_employee}/skills`, {
                  state: { returnTo: `/app/employee-search?${searchParams.toString()}` },
                })}
              >Voir le profil</button>
              { ["MANAGER", "HR"].includes(user?.permission_profile) && Number(user.id_employee) !== Number(employee.id_employee) && <button className="button button-primary" type="button" onClick={() => navigate(`/app/manage-evaluations/${employee.id_employee}`)}>Évaluer</button> }
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
