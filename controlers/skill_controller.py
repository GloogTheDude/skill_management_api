from fastapi import APIRouter, Depends, Query
from core.database import SessionLocal, get_session
from sqlalchemy.orm import Session

from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import CreateSkillDTO, QuerySkillDTO
from services.skill_service import SkillService



router = APIRouter(prefix="/skill",tags=["skill"])
@router.post('/create')
def create_skill(dto: CreateSkillDTO=Query(),
                    session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.create(dto.name, dto.id_domaine)

@router.get('/getall')
def get_all_skills(session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.get_all()

@router.put('/update')
def update_skill(skillDTO: QuerySkillDTO,
                 session:Session = Depends(get_session, scope="function")):
    repo = SkillRepository(session)
    service= SkillService(repo)
    return service.update(skillDTO)

@router.delete('/delete')
def delete_skill(skill_id:int,
                 session:Session = Depends(get_session)):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.delete(skill_id)
    