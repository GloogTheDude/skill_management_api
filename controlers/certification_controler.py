from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.certification_repository import CertificationRepository
from dto.certification_dto import QueryCertificationDTO
from services.certification_service import CertificationService


router = APIRouter(prefix="/certification",tags=["certification"])

@router.post('/certifications')
def create_certification(subject_certification:str=Query(),
                         validity_month:int=Query(),
                         id_domaine:int=Query(),
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.create(subject_certification, validity_month, id_domaine)

@router.get('/certifications/{id_certification}')
def get_certification_by_id(id_certification:int,
                            session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_by_id(id_certification)

@router.get('/certifications')
def get_certifications(session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.get_all()

@router.put('/certifications/{id_certification}')
def update_certification(dto:QueryCertificationDTO,
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.update(dto)

@router.delete('/certifications/{id_certification}')
def delete_certification(id_certification:int,
                         session:Session=Depends(get_session)):
    repo = CertificationRepository(session)
    service= CertificationService(repo)
    return service.delete(id_certification)