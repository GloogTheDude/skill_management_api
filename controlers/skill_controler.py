from fastapi import APIRouter, Body, Depends, Query
from core.database import SessionLocal, get_session
from sqlalchemy.orm import Session

from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import CreateSkillDTO, QuerySkillDTO
from services.skill_service import SkillService



router = APIRouter(prefix="/skill",tags=["skill"])

@router.post('')
def create_skill(dto: CreateSkillDTO=Body(),
                    session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.create(dto.name, dto.id_domaine)

@router.get('/{id_skill}')
def get_skill_by_id(id_skill:int,
                    session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.get_by_id(id_skill)

@router.get('')
def get_all_skills(session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.get_all()

@router.put('')
def update_skill(skillDTO: QuerySkillDTO,
                 session:Session = Depends(get_session, scope="function")):
    repo = SkillRepository(session)
    service= SkillService(repo)
    return service.update(skillDTO)

@router.delete('/{id_skill}')
def delete_skill(id_skill:int,
                 session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.delete(id_skill)
    