
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_session
from db.repositories.diploma_repository import DiplomaRepository
from dto.diploma_dto import CreateDiplomaDTO, UpdateDiplomaDTO,ResponseDiplomaDTO
from services.diploma_service import DiplomaService


router = APIRouter(prefix='/diploma',tags=['diploma'])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_diploma(
    dto:CreateDiplomaDTO,
    session:Session=Depends(get_session)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.create(dto)

@router.get('/{id_diploma}')
def get_diploma_by_id(
    id_diploma:int,
    session:Session=Depends(get_session)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_by_id(id_diploma)

@router.get('')
def get_all_diplomas(session:Session=Depends(get_session))->list[ResponseDiplomaDTO]:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.get_all()

@router.patch('/{id_diploma}')
def update_diploma(
    id_diploma:int,
    dto: UpdateDiplomaDTO,
    session:Session=Depends(get_session)
)->ResponseDiplomaDTO:
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.update(id_diploma, dto)


@router.delete('/{id_diploma}')
def delete_diploma(id_diploma:int,
                   session:Session=Depends(get_session)):
    repo = DiplomaRepository(session)
    service = DiplomaService(repo)
    return service.delete(id_diploma)


    
