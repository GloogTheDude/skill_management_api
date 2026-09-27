
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_session
from db.repositories.diploma_repository import DiplomaRepository
from dto.diploma_dto import CreateDiplomaDTO, UpdateDiplomaDTO,ResponseDiplomaDTO
from services.diploma_service import DiplomaService
from controlers.auth_controller import get_current_employee, require_hr_employee
from dto.skill_link_replacement_dto import ReplaceSkillsDTO
from dto.diploma_skill_dto import ResponseDiplomaSkillDTO
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from services.skill_link_replacement_service import SkillLinkReplacementService


router = APIRouter(prefix='/diploma',tags=['diploma'])


@router.put("s/{id_diploma}/skills", response_model=list[ResponseDiplomaSkillDTO])
def replace_diploma_skills(id_diploma: int, dto: ReplaceSkillsDTO,
                           session: Session = Depends(get_session),
                           _: object = Depends(require_hr_employee)):
    try:
        links = SkillLinkReplacementService(session).replace(
            Diploma, id_diploma, "id_diploma", DiplomaSkill, "id_skill", "min_level",
            [(item.id_skill, item.level) for item in dto.skills],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [ResponseDiplomaSkillDTO.from_entity(link) for link in links]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_diploma(
    dto:CreateDiplomaDTO,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.create(dto)

@router.get('/{id_diploma}')
def get_diploma_by_id(
    id_diploma:int,
    session:Session=Depends(get_session)
    ,_: object = Depends(get_current_employee)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_by_id(id_diploma)

@router.get('')
def get_all_diplomas(session:Session=Depends(get_session), _: object = Depends(get_current_employee))->list[ResponseDiplomaDTO]:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_all()

@router.patch('/{id_diploma}')
def update_diploma(
    id_diploma:int,
    dto: UpdateDiplomaDTO,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.update(id_diploma, dto)


@router.delete('/{id_diploma}')
def delete_diploma(id_diploma:int,
                   session:Session=Depends(get_session),
                   _: object = Depends(require_hr_employee)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.delete(id_diploma)


    
