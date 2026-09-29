function formatDate(value) {
  if (!value) return null;
  return new Intl.DateTimeFormat("fr-BE").format(new Date(`${value}T00:00:00`));
}

function SourceList({ sources }) {
  return (
    <ul className="skill-sources">
      {sources.map((source) => (
        <li key={`${source.source_type}-${source.source_id}`}>
          <span>{source.source_type}</span>
          {source.level !== null && <span>Niveau {source.level}</span>}
          {!source.is_active && <span className="source-inactive">Inactive</span>}
          {source.acquired_at && <span>Acquise le {formatDate(source.acquired_at)}</span>}
          {source.expires_at && <span>Expire le {formatDate(source.expires_at)}</span>}
        </li>
      ))}
    </ul>
  );
}

export default function SkillProfileList({ skills }) {
  return (
    <div className="skills-grid">
      {skills.map((skill) => (
        <article className="skill-card" key={skill.skill_id}>
          <div className="skill-card-header">
            <div>
              <h2>{skill.skill_name}</h2>
              <p>{skill.skill_domaine || "Domaine non renseigné"}</p>
            </div>
            <span className="level-badge">Acquis : {skill.acquired_level ?? "Aucun"}</span>
          </div>
          <p className="primary-source">Évaluation terrain : {skill.evaluated_level ?? "Non évalué"}</p>
          {skill.primary_acquired_source && <p className="primary-source">Acquis principalement via : {skill.primary_acquired_source.source_type}</p>}
          {skill.current_validation && <p className="primary-source">Évalué par : {[skill.current_validation.validator_first_name, skill.current_validation.validator_last_name].filter(Boolean).join(" ") || "Utilisateur"}</p>}
          {skill.sources?.length > 0 && (
            <details>
              <summary>{skill.sources.length} source{skill.sources.length === 1 ? "" : "s"}</summary>
              <SourceList sources={skill.sources} />
            </details>
          )}
        </article>
      ))}
    </div>
  );
}
