from sqlalchemy import select
from sqlalchemy.orm import Session

from models.skill import Skill


class SkillLinkReplacementService:
    def __init__(self, session: Session):
        self.session = session

    def replace(
        self,
        aggregate_model,
        aggregate_id: int,
        aggregate_key: str,
        link_model,
        link_key: str,
        level_key: str,
        requested: list[tuple[int, int | None]],
    ) -> list:
        aggregate = self.session.get(aggregate_model, aggregate_id)
        if aggregate is None or aggregate.is_deleted:
            raise LookupError("Aggregate not found")

        skill_ids = [skill_id for skill_id, _ in requested]
        skills = list(self.session.scalars(select(Skill).where(
            Skill.id_skill.in_(skill_ids), Skill.is_deleted.is_(False)
        )).all()) if skill_ids else []
        if len(skills) != len(skill_ids):
            raise LookupError("Skill not found")

        existing = list(self.session.scalars(select(link_model).where(
            getattr(link_model, aggregate_key) == aggregate_id
        )).all())
        existing_by_skill = {getattr(link, link_key): link for link in existing}
        selected = set()
        for skill_id, level in requested:
            selected.add(skill_id)
            link = existing_by_skill.get(skill_id)
            if link is None:
                link = link_model(**{aggregate_key: aggregate_id, link_key: skill_id})
                self.session.add(link)
            setattr(link, level_key, level)
            link.is_deleted = False

        for link in existing:
            if not link.is_deleted and getattr(link, link_key) not in selected:
                link.is_deleted = True

        self.session.flush()
        return list(self.session.scalars(select(link_model).where(
            getattr(link_model, aggregate_key) == aggregate_id,
            link_model.is_deleted.is_(False),
        )).all())
