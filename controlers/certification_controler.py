from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from core.database import get_session
from db.repositories.certification_repository import CertificationRepository
from dto.certification_dto import CreateCertificationDTO, UpdateCertificationDTO,ResponseCertificationDTO
from services.certification_service import CertificationService


router = APIRouter(prefix="/certification",tags=["certification"])

@router.post('', status_code=status.HTTP_201_CREATED)
def create_certification(
    dto:CreateCertificationDTO,
    session:Session=Depends(get_session)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.create(dto)
    
@router.get('/{id_certification}')
def get_certification_by_id(
    id_certification:int,
    session:Session=Depends(get_session)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_by_id(id_certification)

@router.get('')
def get_certifications(
    session:Session=Depends(get_session)
)->list[ResponseCertificationDTO]:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_all()

@router.patch('/{id_certification}')
def update_certification(
    id_certification:int, 
    dto:UpdateCertificationDTO,
    session:Session=Depends(get_session)
)->ResponseCertificationDTO:
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.update(id_certification, dto)

@router.delete('/{id_certification}')
def delete_certification(
    id_certification:int,
    session:Session=Depends(get_session)
):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.delete(id_certification)