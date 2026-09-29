from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.participation_crud_dto import (
    CloseParticipationDTO,
    CompletableParticipationDTO,
    ParticipationListDTO,
    ResponseParticipationDTO,
)
from dto.participation_document_dto import DocumentType, ResponseParticipationDocumentDTO
from errors.participation_errors import (
    ParticipationCannotCancel,
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
from services.participation_document_service import ParticipationDocumentService


router = APIRouter(
    prefix="/participations",
    tags=["participations"],
)


def _participation_service(session: Session) -> ParticipationService:
    return ParticipationService(ParticipationRepository(session))


def _document_service(session: Session) -> ParticipationDocumentService:
    return ParticipationDocumentService(session)


@router.get(
    "/{id_employee}/{id_training}/documents",
    response_model=list[ResponseParticipationDocumentDTO],
)
def list_participation_documents(
    id_employee: int,
    id_training: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        return _document_service(session).list(current_employee, id_employee, id_training)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation not found") from exc


@router.post(
    "/{id_employee}/{id_training}/documents",
    response_model=ResponseParticipationDocumentDTO,
    status_code=status.HTTP_201_CREATED,
)
async def upload_participation_document(
    id_employee: int,
    id_training: int,
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(require_hr_employee),
):
    try:
        return await _document_service(session).upload(
            current_employee, id_employee, id_training, document_type, file
        )
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/document/{id_document}/download")
def download_participation_document(
    id_document: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
):
    try:
        document, path = _document_service(session).get_for_download(current_employee, id_document)
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (NoResultFound, ValueError) as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return FileResponse(path, media_type=document.mime_type, filename=document.original_filename)


@router.delete("/document/{id_document}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participation_document(
    id_document: int,
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(require_hr_employee),
):
    try:
        _document_service(session).delete(current_employee, id_document)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return None


@router.get("", response_model=list[ParticipationListDTO])
def get_participations(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[ParticipationListDTO]:
    return _participation_service(session).get_all(current_employee.id_employee, current_employee.permission_profile)


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
        EmployeeRepository(session),
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
        EmployeeRepository(session),
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


@router.post(
    "/{id_employee}/{id_training}/close",
    response_model=ResponseParticipationDTO,
)
def close_participation(
    id_employee: int,
    id_training: int,
    dto: CloseParticipationDTO,
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> ResponseParticipationDTO:
    service = ParticipationCompletionService(
        ParticipationRepository(session),
        TrainingRepository(session),
        EmployeeDiplomaRepository(session),
        EmployeeCertificationRepository(session),
        EmployeeRepository(session),
    )
    try:
        participation = service.close(id_employee, id_training, dto.result)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation, Employee or Training not found.") from exc
    except ParticipationInvalidStatus as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except TrainingNotCompleted as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ResponseParticipationDTO.from_entity(participation)


@router.post(
    "/{id_employee}/{id_training}/cancel",
    response_model=ResponseParticipationDTO,
)
def cancel_participation(
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
        EmployeeRepository(session),
    )
    try:
        participation = service.cancel(id_employee, id_training)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Participation, Employee or Training not found.") from exc
    except ParticipationCannotCancel as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ResponseParticipationDTO.from_entity(participation)
