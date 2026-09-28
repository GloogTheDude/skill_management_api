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
            {skill.displayed_level !== null && <span className="level-badge">Niveau {skill.displayed_level}</span>}
          </div>
          {skill.primary_source && <p className="primary-source">Source principale : {skill.primary_source.source_type}</p>}
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
