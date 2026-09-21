from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_repository import TrainingRepository
from dto.training_dto import (
    CreateTrainingDTO,
    UpdateTrainingDTO,
    ResponseTrainingDTO,
)
from services.training_service import TrainingService


router = APIRouter(prefix="/training", tags=["training"])

@router.post('',status_code=201)
def create_training(dto:CreateTrainingDTO,
                    session:Session=Depends(get_session))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.create(dto)

@router.get('/{id_training}')
def get_training_by_id(id_training:int,
                       session:Session=Depends(get_session))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.get_by_id(id_training)

@router.get('')
def get_trainings(session:Session=Depends(get_session))->list[ResponseTrainingDTO]:
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.get_all()

@router.patch(
    "/{id_training}",
    response_model=ResponseTrainingDTO
)
def update_training(id_training:int, 
                    dto:UpdateTrainingDTO,
                    session:Session=Depends(get_session))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.update(id_training, dto)

@router.delete('/{id_training}')
def delete_training(id_training:int,
                    session: Session=Depends(get_session)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.delete(id_training)

