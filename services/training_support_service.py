from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.skill import Skill
from models.training import Training
from models.training_skill import TrainingSkill
from db.repositories.training_repository import TrainingRepository
from errors.training_errors import TrainingLifecycleConflict


class TrainingSupportService:
    """Validates and synchronizes the support of a Training."""

    def __init__(self, session: Session):
        self.session = session

    def validate_support(self, id_diploma, id_certification, skill_ids: list[int]) -> None:
        if id_diploma is not None and id_certification is not None:
            raise ValueError("A training cannot have both a diploma and a certification.")
        if (id_diploma is not None or id_certification is not None) and skill_ids:
            raise ValueError("A training with a diploma or certification cannot have direct training skills.")
        if id_diploma is None and id_certification is None and not skill_ids:
            raise ValueError("A training must have a diploma, certification, or skill.")

        if skill_ids:
            skills = list(self.session.scalars(select(Skill).where(
                Skill.id_skill.in_(skill_ids),
                Skill.is_deleted.is_(False),
            )).all())
            if len(skills) != len(set(skill_ids)):
                raise LookupError("Skill not found")

    def validate_final_state(self, id_training, id_diploma, id_certification, skill_ids=None) -> None:
        if skill_ids is None:
            active_count = self.session.scalar(select(func.count()).select_from(TrainingSkill).where(
                TrainingSkill.id_training == id_training,
                TrainingSkill.is_deleted.is_(False),
            ))
            if (id_diploma is not None or id_certification is not None) and active_count:
                raise ValueError("A training with a diploma or certification cannot have direct training skills.")
            if id_diploma is None and id_certification is None and not active_count:
                raise ValueError("A training must have a diploma, certification, or skill.")
            return
        self.validate_support(id_diploma, id_certification, skill_ids)

    def is_used(self, id_training: int) -> bool:
        return TrainingRepository(self.session).is_used(id_training)

    def replace_skills(
        self,
        id_training: int,
        requested: list[tuple[int, int]],
    ) -> list[TrainingSkill]:
        training = self.session.get(Training, id_training)
        if training is None or training.is_deleted:
            raise LookupError("Training not found")
        if self.is_used(id_training):
            raise TrainingLifecycleConflict("Training skills cannot be changed after the training is used.")

        self.validate_support(
            training.id_diploma,
            training.id_certification,
            [skill_id for skill_id, _ in requested],
        )

        existing = list(self.session.scalars(select(TrainingSkill).where(
            TrainingSkill.id_training == id_training,
        )).all())
        existing_by_skill = {link.id_skill: link for link in existing}
        selected = {skill_id for skill_id, _ in requested}

        for skill_id, level in requested:
            link = existing_by_skill.get(skill_id)
            if link is None:
                link = TrainingSkill(id_training=id_training, id_skill=skill_id)
                self.session.add(link)
            link.granted_level = level
            link.is_deleted = False

        for link in existing:
            if not link.is_deleted and link.id_skill not in selected:
                link.is_deleted = True

        self.session.flush()
        return list(self.session.scalars(select(TrainingSkill).where(
            TrainingSkill.id_training == id_training,
            TrainingSkill.is_deleted.is_(False),
        )).all())

    def validate_link_deletion(self, id_training: int, id_skill: int) -> None:
        training = self.session.get(Training, id_training)
        if training is None or training.is_deleted:
            raise LookupError("Training not found")
        if training.id_diploma is not None or training.id_certification is not None:
            return

        remaining = self.session.scalar(select(func.count()).select_from(TrainingSkill).where(
            TrainingSkill.id_training == id_training,
            TrainingSkill.id_skill != id_skill,
            TrainingSkill.is_deleted.is_(False),
        ))
        if not remaining:
            raise ValueError("A training must retain a diploma, certification, or skill.")
