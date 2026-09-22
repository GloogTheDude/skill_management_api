from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import CreateSkillDTO, UpdateSkillDTO, ResponseSkillDTO
from models.skill import Skill
from services.base_crud_service import BaseCrudService


class SkillService(BaseCrudService[Skill]):

    def create(
        self,
        dto: CreateSkillDTO
    )-> ResponseSkillDTO:
        skill = Skill(
            name_skill=dto.name_skill,
            id_domaine=dto.id_domaine,
        )

        skill = self.repository.add(skill)

        return ResponseSkillDTO.from_entity(skill)

    def get_all(self) -> list[ResponseSkillDTO]:
        skills = self._get_all_entities()
        return [
            ResponseSkillDTO.from_entity(skill)
            for skill in skills
        ]

    def get_by_id(
        self, 
        id_skill: int
    ) -> ResponseSkillDTO:
        skill = self._get_entity_by_id(id_skill)

        return ResponseSkillDTO.from_entity(skill)

    def update(
        self,
        id_skill: int,
        dto: UpdateSkillDTO,
    ) -> ResponseSkillDTO:
        data = dto.model_dump(exclude_unset=True)
        skill = self.repository.update(
            id_skill,
            **data,
        )
        return ResponseSkillDTO.from_entity(skill)