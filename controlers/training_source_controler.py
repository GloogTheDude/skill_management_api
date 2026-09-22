from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_source_dto import (
    CreateTrainingSourceDTO,
    UpdateTrainingSourceDTO,
    ResponseTrainingSourceDTO,
)
from services.training_source_service import TrainingSourceService


router = APIRouter(
    prefix="/training_source",
    tags=["training_source"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_training_source(
    dto: CreateTrainingSourceDTO,
    session: Session = Depends(get_session),
) -> ResponseTrainingSourceDTO:
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.create(dto)


@router.get("/{id_source}")
def get_training_source_by_id(
    id_source: int,
    session: Session = Depends(get_session),
) -> ResponseTrainingSourceDTO:
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.get_by_id(id_source)


@router.get("")
def get_training_sources(
    session: Session = Depends(get_session),
) -> list[ResponseTrainingSourceDTO]:
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.get_all()


@router.patch("/{id_source}")
def update_training_source(
    id_source: int,
    dto: UpdateTrainingSourceDTO,
    session: Session = Depends(get_session),
) -> ResponseTrainingSourceDTO:
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.update(id_source, dto)


@router.delete("/{id_source}")
def delete_training_source(
    id_source: int,
    session: Session = Depends(get_session),
):
    repo = TrainingSourceRepository(session)
    service = TrainingSourceService(repo)
    return service.delete(id_source)