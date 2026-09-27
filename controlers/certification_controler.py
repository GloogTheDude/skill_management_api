from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from core.database import get_session
from db.repositories.certification_repository import CertificationRepository
from dto.certification_dto import CreateCertificationDTO, UpdateCertificationDTO,ResponseCertificationDTO
from services.certification_service import CertificationService
from controlers.auth_controller import get_current_employee, require_hr_employee
from dto.skill_link_replacement_dto import ReplaceSkillsDTO
from dto.certification_skill_dto import ResponseCertificationSkillDTO
from models.certification import Certification
from models.certification_skill import CertificationSkill
from services.skill_link_replacement_service import SkillLinkReplacementService


router = APIRouter(prefix="/certification",tags=["certification"])


@router.put("s/{id_certification}/skills", response_model=list[ResponseCertificationSkillDTO])
def replace_certification_skills(id_certification: int, dto: ReplaceSkillsDTO,
                                 session: Session = Depends(get_session),
                                 _: object = Depends(require_hr_employee)):
    try:
        links = SkillLinkReplacementService(session).replace(
            Certification, id_certification, "id_certification", CertificationSkill,
            "id_skill", "granted_level", [(item.id_skill, item.level) for item in dto.skills],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [ResponseCertificationSkillDTO.from_entity(link) for link in links]

@router.post('', status_code=status.HTTP_201_CREATED)
def create_certification(
    dto:CreateCertificationDTO,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.create(dto)
    
@router.get('/{id_certification}')
def get_certification_by_id(
    id_certification:int,
    session:Session=Depends(get_session)
    ,_: object = Depends(get_current_employee)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_by_id(id_certification)

@router.get('')
def get_certifications(
    session:Session=Depends(get_session)
    ,_: object = Depends(get_current_employee)
)->list[ResponseCertificationDTO]:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_all()

@router.patch('/{id_certification}')
def update_certification(
    id_certification:int, 
    dto:UpdateCertificationDTO,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.update(id_certification, dto)

@router.delete('/{id_certification}')
def delete_certification(
    id_certification:int,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.delete(id_certification)
