import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
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

export default function EmployeeSkillSearchPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();
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
    setSearching(true);
    setError(null);
    try {
      const payload = requirements.map((requirement) => ({
        id_skill: Number(requirement.id_skill),
        operator: requirement.operator,
        level: Number(requirement.level),
      }));
      setResults(await searchEmployeesBySkills(payload));
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        await logout().catch(() => undefined);
        navigate("/login", { replace: true });
        return;
      }
      setError(requestError instanceof ApiError && requestError.status === 403
        ? "Vous n’êtes pas autorisé à effectuer cette recherche."
        : requestError instanceof ApiError && requestError.status === 422 && requestError.detail
          ? requestError.detail
          : "La recherche n’a pas pu être effectuée. Réessayez plus tard.");
    } finally {
      setSearching(false);
    }
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
              Niveau
              <select value={requirement.operator} onChange={(event) => updateRequirement(index, "operator", event.target.value)}>
                <option value="gte">Au moins</option>
                <option value="gt">Supérieur à</option>
                <option value="eq">Égal à</option>
              </select>
            </label>
            <label>
              Valeur (1–5)
              <input type="number" min="1" max="5" value={requirement.level} onChange={(event) => updateRequirement(index, "level", event.target.value)} />
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
                  <span>Niveau affiché : {skill.displayed_level ?? "non renseigné"}</span>
                  {skill.sources.length > 0 && <ul className="skill-sources">{skill.sources.map((source) => <li key={`${source.source_type}-${source.source_id}`}>{sourceLabel(source)}</li>)}</ul>}
                </div>
              ))}
              <button className="button button-secondary" type="button" onClick={() => navigate(`/app/employees/${employee.id_employee}/skills`)}>Voir le profil</button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
