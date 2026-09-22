from dto.certification_skill_dto import (
    CreateCertificationSkillDTO,
    UpdateCertificationSkillDTO,
    ResponseCertificationSkillDTO,
)
from models.certification_skill import CertificationSkill
from services.base_crud_service import BaseCrudService


class CertificationSkillService(BaseCrudService[CertificationSkill]):

    def get_all(self) -> list[ResponseCertificationSkillDTO]:
        certification_skills = self._get_all_entities()

        return [
            ResponseCertificationSkillDTO.from_entity(cs)
            for cs in certification_skills
        ]

    def get_by_id(
        self,
        id_certification: int,
        id_skill: int,
    ) -> ResponseCertificationSkillDTO:

        cs = self._get_entity_by_id(
            (id_certification, id_skill)
        )

        return ResponseCertificationSkillDTO.from_entity(cs)

    def create(
        self,
        dto: CreateCertificationSkillDTO,
    ) -> ResponseCertificationSkillDTO:

        cs = CertificationSkill(
            id_certification=dto.id_certification,
            id_skill=dto.id_skill,
            granted_level=dto.granted_level,
        )

        created = self.repository.add(cs)

        return ResponseCertificationSkillDTO.from_entity(created)

    def update(
        self,
        id_certification: int,
        id_skill: int,
        dto: UpdateCertificationSkillDTO,
    ) -> ResponseCertificationSkillDTO:

        data = dto.model_dump(exclude_unset=True)

        cs = self.repository.update(
            (id_certification, id_skill),
            **data,
        )

        return ResponseCertificationSkillDTO.from_entity(cs)