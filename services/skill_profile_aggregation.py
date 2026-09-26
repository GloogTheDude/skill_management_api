from dto.skill_dto import SkillProfileDTO, SkillSourceDTO


def add_skill_source(
    profiles: dict[int, SkillProfileDTO],
    *,
    skill_id: int,
    skill_name: str,
    skill_domaine: str | None,
    source: SkillSourceDTO,
) -> None:
    profile = profiles.get(skill_id)
    if profile is None:
        profiles[skill_id] = SkillProfileDTO(
            skill_id=skill_id,
            skill_name=skill_name,
            skill_domaine=skill_domaine,
            displayed_level=source.level,
            primary_source=source,
            sources=[source],
        )
        return

    profile.sources.append(source)
    if should_replace_primary_source(source, profile.primary_source):
        profile.primary_source = source
        profile.displayed_level = source.level


def should_replace_primary_source(
    new_source: SkillSourceDTO,
    current_source: SkillSourceDTO | None,
) -> bool:
    if current_source is None:
        return True
    if new_source.is_active != current_source.is_active:
        return new_source.is_active
    if new_source.level is None:
        return False
    if current_source.level is None:
        return True
    return new_source.level > current_source.level
