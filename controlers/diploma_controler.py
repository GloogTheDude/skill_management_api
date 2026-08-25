
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.diploma_repository import DiplomaRepository
from dto.diploma_dto import QueryDiplomaDTO
from services.diploma_service import DiplomaService


router = APIRouter(prefix='/diploma',tags=['diploma'])

@router.post('')
def create_diploma(dto:QueryDiplomaDTO,
                   session:Session=Depends(get_session)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.create(dto.subject_diploma,
                          dto.level_diploma,
                          dto.id_domaine)

@router.get('/id_diploma')
def get_diploma_by_id(id_diploma:int,
                      session:Session=Depends(get_session)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_by_id(id_diploma)

@router.get('')
def get_all_diplomas(session:Session=Depends(get_session)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_all()

@router.delete('{id_diploma}')
def delete_diploma(id_diploma:int,
                   session:Session=Depends(get_session)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.delete(id_diploma)
    
