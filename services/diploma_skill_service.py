from dto.diploma_skill_dto import (
    CreateDiplomaSkillDTO,
    UpdateDiplomaSkillDTO,
    ResponseDiplomaSkillDTO,
)
from models.diploma_skill import DiplomaSkill
from services.base_crud_service import BaseCrudService


class DiplomaSkillService(BaseCrudService[DiplomaSkill]):

    def get_all(self) -> list[ResponseDiplomaSkillDTO]:
        diploma_skills = self._get_all_entities()

        return [
            ResponseDiplomaSkillDTO.from_entity(ds)
            for ds in diploma_skills
        ]

    def get_by_id(
        self,
        id_diploma: int,
        id_skill: int,
    ) -> ResponseDiplomaSkillDTO:

        ds = self._get_entity_by_id(
            (id_diploma, id_skill)
        )

        return ResponseDiplomaSkillDTO.from_entity(ds)

    def create(
        self,
        dto: CreateDiplomaSkillDTO,
    ) -> ResponseDiplomaSkillDTO:

        ds = DiplomaSkill(
            id_diploma=dto.id_diploma,
            id_skill=dto.id_skill,
            min_level=dto.min_level,
        )

        created = self.repository.add(ds)

        return ResponseDiplomaSkillDTO.from_entity(created)

    def update(
        self,
        id_diploma: int,
        id_skill: int,
        dto: UpdateDiplomaSkillDTO,
    ) -> ResponseDiplomaSkillDTO:

        data = dto.model_dump(exclude_unset=True)

        ds = self.repository.update(
            (id_diploma, id_skill),
            **data,
        )

        return ResponseDiplomaSkillDTO.from_entity(ds)