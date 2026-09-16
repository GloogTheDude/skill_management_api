from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_repository import TrainingRepository
from dto.training_dto import QueryTrainingDTO, CreateTrainingDTO
from services.training_service import TrainingService


router = APIRouter(prefix="/training", tags=["training"])

@router.post('')
def create_training(dto:CreateTrainingDTO,
                    session:Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.create(dto)

@router.get('/{id_training}')
def get_training_by_id(id_training:int,
                       session:Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.get_by_id(id_training)

@router.get('')
def get_trainings(session:Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.get_all()

@router.put('/update/{id}')
def update_training(id:int, dto:QueryTrainingDTO,
                    session:Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.update(id, dto)

@router.delete('/{id_training}')
def delete_training(id_training:int,
                    session: Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.delete(id_training)

