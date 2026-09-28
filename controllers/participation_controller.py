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
    ParticipationListDTO,
    ResponseParticipationDTO,
)
from errors.participation_errors import (
    ParticipationCannotStart,
    ParticipationInvalidStatus,
    TrainingNotCompleted,
)
from services.participation_completion_service import ParticipationCompletionService
from services.participation_service import ParticipationService
from controllers.auth_controller import get_current_employee, require_hr_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from models.employee import Employee
from services.employee_authorization_service import EmployeeAuthorizationService


router = APIRouter(
    prefix="/participations",
    tags=["participations"],
)


def _participation_service(session: Session) -> ParticipationService:
    return ParticipationService(ParticipationRepository(session))


@router.get("", response_model=list[ParticipationListDTO])
def get_participations(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ParticipationListDTO]:
    return _participation_service(session).get_all(current_employee.id_employee, current_employee.access_level)


@router.get("/completable", response_model=list[CompletableParticipationDTO])
def get_completable_participations(
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
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
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> ResponseParticipationDTO:
    try:
        result = _participation_service(session).get_by_id(id_employee, id_training)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation not found") from exc
    target = session.get(Employee, result.id_employee)
    if target is None or target.is_deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        EmployeeAuthorizationService.require_self_or_direct_manager_or_hr(current_employee, target)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return result


@router.delete("/{id_employee}/{id_training}")
def delete_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
):
    repository = ParticipationRepository(session)
    try:
        participation = repository.get_one((id_employee, id_training))
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation not found") from exc
    if participation.is_deleted:
        raise HTTPException(status_code=404, detail="Participation not found")
    return repository.soft_delete((id_employee, id_training))


@router.post(
    "/{id_employee}/{id_training}/start",
    response_model=ResponseParticipationDTO,
)
def start_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseParticipationDTO:
    service = ParticipationCompletionService(
        ParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
    )
    try:
        participation = service.start(id_employee, id_training)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation or Training not found.") from exc
    except ParticipationCannotStart as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ResponseParticipationDTO.from_entity(participation)


@router.post(
    "/{id_employee}/{id_training}/complete",
    response_model=ResponseParticipationDTO,
)
def complete_participation(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseParticipationDTO:
    service = ParticipationCompletionService(
        ParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
    )

    try:
        participation = service.complete(id_employee, id_training)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation or Training not found.") from exc
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
