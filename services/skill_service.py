from fastapi import HTTPException

from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import QuerySkillDTO, ResponseSkillDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from errors.skill_errors import ErrorIDSkillMissing, ErrorSkillAlreadyDeleted
from models.skill import Skill


class SkillService():
    def __init__(self, skill_repo:SkillRepository):
        self.skill_repository = skill_repo

    def create(self, name_skill: str, id_domaine: int | None) -> Skill:
        try:
            return self.skill_repository.add(name_skill,id_domaine)
        except ErrorIDDomaineMissing:
            raise HTTPException(
            status_code=404,
            detail="NO DOMAINE FOR THAT ID"
            ) 

    def update(
            self,
            skill_dto:QuerySkillDTO
        ) -> Skill | None:
        print("will try to update")
        try:
            print("trying to update")
            self.skill_repository.update(skill_dto)
        except ErrorIDSkillMissing:
            raise HTTPException(
                status_code=404,
                detail="SKILL MISSING"
                )
        except ErrorIDDomaineMissing:
            raise HTTPException(
                status_code=404,
                detail='NO DOMAINE FOR THAT ID'
            )
    
    def delete(self, id_skill: int) -> bool:
        try:
            self.skill_repository.soft_delete(id_skill)
        except ErrorIDSkillMissing:
            raise HTTPException(
                status_code=404,
                detail="ID SKILL MISSING"
                )
        except ErrorSkillAlreadyDeleted:
            raise HTTPException(
                status_code=404,
                detail='SKILL ALREADY DELETED'
            )
        return True

    def get_all(self)->list[ResponseSkillDTO]:
        rows = self.skill_repository.get_all()
        arr = []
        for row in rows:
            arr.append(ResponseSkillDTO.from_entity(row))
        return arr
            
            
        
