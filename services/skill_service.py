from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import QuerySkillDTO, ResponseSkillDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from errors.generic_errors import EntityAlreadyDeleted
from errors.skill_errors import ErrorIDSkillMissing, ErrorSkillAlreadyDeleted
from models.skill import Skill
from services.base_crud_service import BaseCrudService


class SkillService(BaseCrudService[Skill]):

    def create(self,name_skill: str,id_domaine: int,) -> Skill:
        skill = Skill(
            name_skill=name_skill,
            id_domaine=id_domaine,
        )
        return self.repository.add(skill)

    def get_all(self) -> list[ResponseSkillDTO]:
        skills = self._get_all_entities()
        return [
            ResponseSkillDTO.from_entity(skill)
            for skill in skills
        ]

    def get_by_id(self, id_skill: int) -> ResponseSkillDTO:
        skill = self._get_entity_by_id(id_skill)

        return ResponseSkillDTO.from_entity(skill)

    def update(self,dto: QuerySkillDTO,) -> Skill:
        return self.repository.update(
            dto.id_skill,
            name_skill=dto.name_skill,
            id_domaine=dto.id_domaine,
        )