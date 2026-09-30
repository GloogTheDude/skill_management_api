function formatDate(value) {
  if (!value) return null;
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function SourceList({ sources }) {
  const sourceLabels = { TRAINING: "Formation", DIPLOMA: "Diplôme", CERTIFICATION: "Certification", VALIDATION: "Évaluation" };
  return (
    <ul className="skill-sources">
      {sources.map((source) => (
        <li key={`${source.source_type}-${source.source_id}`}>
          <span>{sourceLabels[source.source_type] || source.source_type}</span>
          {source.level !== null && <span>Niveau {source.level}</span>}
          {!source.is_active && <span className="source-inactive">Inactive</span>}
          {source.acquired_at && <span>Acquise le {formatDate(source.acquired_at)}</span>}
          {source.expires_at && <span>Expire le {formatDate(source.expires_at)}</span>}
        </li>
      ))}
    </ul>
  );
}

export default function SkillProfileList({ skills, canEvaluate = false, onEvaluate, onHistory }) {
  return (
    <div className="skills-grid">
      {skills.map((skill) => (
        <article className="skill-card" key={skill.skill_id}>
          <div className="skill-card-header">
            <div>
              <h2>{skill.skill_name}</h2>
              <p>{skill.skill_domaine || "Domaine non renseigné"}</p>
            </div>
            <div className="skill-levels">
              <span className="level-badge">Niveau acquis : {skill.acquired_level ?? "Aucun"} / 5</span>
              <span className="level-badge level-badge-secondary">Niveau évalué : {skill.evaluated_level ?? "Non évalué"}{skill.evaluated_level !== null && skill.evaluated_level !== undefined ? " / 5" : ""}</span>
            </div>
          </div>
          {skill.primary_acquired_source && <p className="primary-source">Acquis principalement via : {{ TRAINING: "Formation", DIPLOMA: "Diplôme", CERTIFICATION: "Certification" }[skill.primary_acquired_source.source_type] || skill.primary_acquired_source.source_type}</p>}
          {canEvaluate && (
            <div className="card-actions">
              <button className="button button-secondary" type="button" onClick={() => onEvaluate(skill)}>
                {skill.current_validation ? "Réévaluer" : "Évaluer"}
              </button>
              <button className="button button-secondary" type="button" onClick={() => onHistory(skill)}>
                Historique
              </button>
            </div>
          )}
          <details>
            <summary>Voir les détails</summary>
            {skill.sources?.length > 0 && <><h3>Sources d’acquisition</h3><SourceList sources={skill.sources} /></>}
            {skill.current_validation && <><h3>Dernière évaluation</h3><p>Niveau : {skill.current_validation.level}</p><p>Évalué par : {[skill.current_validation.validator_first_name, skill.current_validation.validator_last_name].filter(Boolean).join(" ") || "Utilisateur"}</p>{skill.current_validation.justification && <p>Justification : « {skill.current_validation.justification} »</p>}</>}
          </details>
        </article>
      ))}
    </div>
  );
}
