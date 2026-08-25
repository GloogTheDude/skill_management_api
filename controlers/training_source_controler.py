

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_source_dto import QueryTrainingSourceDTO
from services.training_source_service import TrainingSourceService

router = APIRouter(prefix="/training_source",tags=["training_source"])

@router.post("")
def create_training_source(name_source:str,
                           session:Session = Depends(get_session)):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    service.create(name_source)

@router.get('/{id_training_sources}')
def get_training_sources_by_id(id_training_source:int,
                    session:Session = Depends(get_session)):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.get_by_id(id_training_source)


@router.get('')
def get_training_sources(session:Session = Depends(get_session)):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.get_all()


@router.put('')
def update_training_sources(dto:QueryTrainingSourceDTO,
                            session:Session = Depends(get_session)):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    service.update(dto)

@router.delete('/{id_training_source}')
def delete_training_sources(id_training_source:int,
                            session:Session = Depends(get_session)):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    service.delete(id_training_source)