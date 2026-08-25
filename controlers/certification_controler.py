from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.certification_repository import CertificationRepository
from dto.certification_dto import CreateCertificationDTO, QueryCertificationDTO
from services.certification_service import CertificationService


router = APIRouter(prefix="/certification",tags=["certification"])

@router.post('')
def create_certification(dto:CreateCertificationDTO,
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.create(dto.subject_certification, # type: ignore
                          dto.validity_month, # type: ignore
                          dto.id_domaine) # type: ignore

@router.get('/{id_certification}')
def get_certification_by_id(id_certification:int,
                            session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_by_id(id_certification)

@router.get('')
def get_certifications(session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_all()

@router.put('')
def update_certification(dto:QueryCertificationDTO,
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.update(dto)

@router.delete('{id_certification}')
def delete_certification(id_certification:int,
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.delete(id_certification)