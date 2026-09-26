from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from dto.participation_crud_dto import (
    CompletableParticipationDTO,
    ResponseParticipationDTO,
)
from errors.participation_errors import (
    ParticipationInvalidStatus,
    TrainingNotCompleted,
)
from services.participation_completion_service import ParticipationCompletionService
from services.participation_service import ParticipationService


router = APIRouter(
    prefix="/participations",
    tags=["participations"],
)


def _participation_service(session: Session) -> ParticipationService:
    return ParticipationService(ParticipationRepository(session))


@router.get("", response_model=list[ResponseParticipationDTO])
def get_participations(
    session: Session = Depends(get_session),
) -> list[ResponseParticipationDTO]:
    return _participation_service(session).get_all()


@router.get("/completable", response_model=list[CompletableParticipationDTO])
def get_completable_participations(
    session: Session = Depends(get_session),
) -> list[CompletableParticipationDTO]:
    return _participation_service(session).get_completable()


@router.get(
    "/{id_employee}/{id_training}",
    response_model=ResponseParticipationDTO,
)
def get_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
) -> ResponseParticipationDTO:
    return _participation_service(session).get_by_id(id_employee, id_training)


@router.delete("/{id_employee}/{id_training}")
def delete_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
):
    repository = ParticipationRepository(session)
    participation = repository.get_one((id_employee, id_training))
    if participation.is_deleted:
        raise NoResultFound()
    return repository.soft_delete((id_employee, id_training))


@router.post(
    "/{id_employee}/{id_training}/complete",
    response_model=ResponseParticipationDTO,
)
def complete_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
) -> ResponseParticipationDTO:
    service = ParticipationCompletionService(
        ParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
    )

    try:
        participation = service.complete(id_employee, id_training)
    except ParticipationInvalidStatus as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except TrainingNotCompleted as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return ResponseParticipationDTO.from_entity(participation)
