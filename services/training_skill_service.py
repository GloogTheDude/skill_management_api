from dto.training_skill_dto import (
    UpdateTrainingSkillDTO,
    CreateTrainingSkillDTO,
    ResponseTrainingSkillDTO,
)
from models.training_skill import TrainingSkill
from services.base_crud_service import BaseCrudService


class TrainingSkillService(BaseCrudService[TrainingSkill]):

    def get_all(self) -> list[ResponseTrainingSkillDTO]:
        training_skills = self._get_all_entities()

        return [
            ResponseTrainingSkillDTO.from_entity(ts)
            for ts in training_skills
        ]

    def get_by_id(
        self,
        id_training: int,
        id_skill: int,
    ) -> ResponseTrainingSkillDTO:

        ts = self.repository.get_one(
            (id_skill, id_training)
        )

        return ResponseTrainingSkillDTO.from_entity(ts)

    def create(
        self,
        dto: CreateTrainingSkillDTO,
    ) -> ResponseTrainingSkillDTO:

        ts = TrainingSkill(
            id_skill=dto.id_skill,
            id_training=dto.id_training,
            granted_level=dto.granted_level,
        )

        created = self.repository.add(ts)

        return ResponseTrainingSkillDTO.from_entity(created)

    def update(
        self,
        id_training: int,
        id_skill: int,
        dto: UpdateTrainingSkillDTO,
    ) -> ResponseTrainingSkillDTO:

        data = dto.model_dump(exclude_unset=True)

        ts = self.repository.update(
            (id_skill, id_training),
            **data,
        )

        return ResponseTrainingSkillDTO.from_entity(ts)