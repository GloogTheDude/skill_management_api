from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from controlers.auth_controller import get_current_employee
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_request_repository import TrainingRequestRepository
from dto.training_request_api_dto import (
    ApproveTrainingRequestDTO,
    CreatePersonalizedTrainingRequestDTO,
    CreatePlannedTrainingRequestDTO,
    RejectTrainingRequestDTO,
    ResponseTrainingRequestDTO,
    PendingTrainingRequestDTO,
)
from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import (
    ActiveParticipationConflict,
    RelatedEntityNotFound,
    TrainingRequestConflict,
    TrainingRequestNotFound,
    TrainingRequestForbidden,
)
from services.training_request_service import TrainingRequestService
from services.training_request_workflow_service import TrainingRequestWorkflowService
from services.training_request_queue_service import TrainingRequestQueueService


router = APIRouter(prefix="/training-requests", tags=["training-requests"])


def _repositories(session: Session):
    return (
        TrainingRequestRepository(session),
        EmployeeRepository(session),
        TrainingRepository(session),
        ParticipationRepository(session),
    )


def _workflow(session: Session) -> TrainingRequestWorkflowService:
    return TrainingRequestWorkflowService(*_repositories(session))


@router.post("/planned", response_model=ResponseTrainingRequestDTO, status_code=201)
def create_planned(
    dto: CreatePlannedTrainingRequestDTO,
    session: Session = Depends(get_session),
):
    try:
        return TrainingRequestService(
            TrainingRequestRepository(session),
            EmployeeRepository(session),
            TrainingRepository(session),
        ).create_planned(dto)
    except RelatedEntityNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/personalized", response_model=ResponseTrainingRequestDTO, status_code=201)
def create_personalized(
    dto: CreatePersonalizedTrainingRequestDTO,
    session: Session = Depends(get_session),
):
    try:
        return TrainingRequestService(
            TrainingRequestRepository(session),
            EmployeeRepository(session),
            TrainingRepository(session),
        ).create_personalized(dto)
    except RelatedEntityNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("", response_model=list[ResponseTrainingRequestDTO])
def get_training_requests(
    session: Session = Depends(get_session),
):
    return TrainingRequestService(TrainingRequestRepository(session)).get_all()


@router.get("/pending/manager", response_model=list[PendingTrainingRequestDTO])
def get_pending_manager_requests(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        return TrainingRequestQueueService(
            TrainingRequestRepository(session)
        ).get_for_manager(current_employee)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/pending/hr", response_model=list[PendingTrainingRequestDTO])
def get_pending_hr_requests(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        return TrainingRequestQueueService(
            TrainingRequestRepository(session)
        ).get_for_hr(current_employee)
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/mine", response_model=list[ResponseTrainingRequestDTO])
def get_my_training_requests(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    return TrainingRequestService(
        TrainingRequestRepository(session)
    ).get_mine(current_employee)


@router.get("/{id_training_request}", response_model=ResponseTrainingRequestDTO)
def get_training_request(
    id_training_request: int,
    session: Session = Depends(get_session),
):
    try:
        return TrainingRequestService(TrainingRequestRepository(session)).get_by_id(
            id_training_request
        )
    except TrainingRequestNotFound as exc:
        raise HTTPException(status_code=404, detail="Training request not found.") from exc


@router.post("/{id_training_request}/approve", response_model=ResponseTrainingRequestDTO)
def approve_training_request(
    id_training_request: int,
    dto: ApproveTrainingRequestDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        return _workflow(session).approve(id_training_request, dto, current_employee)
    except TrainingRequestNotFound as exc:
        raise HTTPException(status_code=404, detail="Training request not found.") from exc
    except RelatedEntityNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (TrainingRequestConflict, ActiveParticipationConflict) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/{id_training_request}/reject", response_model=ResponseTrainingRequestDTO)
def reject_training_request(
    id_training_request: int,
    dto: RejectTrainingRequestDTO,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        return _workflow(session).reject(id_training_request, dto, current_employee)
    except TrainingRequestNotFound as exc:
        raise HTTPException(status_code=404, detail="Training request not found.") from exc
    except RelatedEntityNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TrainingRequestConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except TrainingRequestForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
