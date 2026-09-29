from datetime import date

from dto.skill_dto import SkillProfileDTO, SkillSourceDTO
from core.constants import SKILLSOURCETYPE


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


def finalize_skill_dimensions(profile: SkillProfileDTO) -> None:
    acquired = [
        source for source in profile.sources
        if source.source_type != SKILLSOURCETYPE.VALIDATION.value
        and source.is_active
    ]
    profile.acquired_sources = [
        source for source in profile.sources
        if source.source_type != SKILLSOURCETYPE.VALIDATION.value
    ]
    profile.acquired_level = max(
        (source.level for source in acquired if source.level is not None),
        default=None,
    )
    if acquired:
        profile.primary_acquired_source = sorted(
            acquired,
            key=lambda source: (
                source.level is not None,
                source.level if source.level is not None else -1,
                source.acquired_at or date.min,
                source.source_type,
                source.source_id,
            ),
            reverse=True,
        )[0]
    validation = next(
        (source for source in profile.sources
         if source.source_type == SKILLSOURCETYPE.VALIDATION.value
         and source.is_active),
        None,
    )
    profile.evaluated_level = validation.level if validation else None
