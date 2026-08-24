

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.domaine_repository import DomaineRepository
from dto.domaine_dto import QueryDomaineDTO
from services.domaine_service import DomaineService


router = APIRouter(prefix="/domaine",tags=["domaine"])

@router.post('/domaines')
def create_domaine(name_domaine:str=Body(),
                   session:Session=Depends(get_session)):
    repo = DomaineRepository(session)
    service= DomaineService(repo)
    return service.create(name_domaine)

@router.get('/domaines/{id_domaine}')
def get_domaine_by_id(id_domaine:int,
                      session:Session=Depends(get_session)):
    repo = DomaineRepository(session)
    service= DomaineService(repo)
    return service.get_by_id(id_domaine)

@router.get('/domaines')
def get_domaines(session:Session=Depends(get_session)):
    repo = DomaineRepository(session)
    service= DomaineService(repo)
    return service.get_all()


@router.put('/domaines')
def update_domaine(dto:QueryDomaineDTO,
                   session:Session=Depends(get_session)):
    repo = DomaineRepository(session)
    service= DomaineService(repo)
    service.update(dto)

@router.delete('/domaines/{id_domaine}')
def delete_domaine(id_domaine:int,
                   session:Session=Depends(get_session)):
    repo = DomaineRepository(session)
    service= DomaineService(repo)
    service.delete(id_domaine)

