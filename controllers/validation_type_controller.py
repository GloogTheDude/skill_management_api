from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.validation_type_repository import ValidationTypeRepository
from dto.validation_type_dto import (
    CreateValidationTypeDTO,
    UpdateValidationTypeDTO,
    ResponseValidationTypeDTO,
)
from services.validation_type_service import ValidationTypeService
from controllers.auth_controller import get_current_employee, require_hr_employee


router = APIRouter(
    prefix="/validation_type",
    tags=["validation_type"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_validation_type(
    dto: CreateValidationTypeDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseValidationTypeDTO:
    repo = ValidationTypeRepository(session)
    service = ValidationTypeService(repo)
    return service.create(dto)


@router.get("/{id_validation}")
def get_validation_type_by_id(
    id_validation: int,
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> ResponseValidationTypeDTO:
    repo = ValidationTypeRepository(session)
    service = ValidationTypeService(repo)
    return service.get_by_id(id_validation)


@router.get("")
def get_validation_types(
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> list[ResponseValidationTypeDTO]:
    repo = ValidationTypeRepository(session)
    service = ValidationTypeService(repo)
    return service.get_all()


@router.patch("/{id_validation}")
def update_validation_type(
    id_validation: int,
    dto: UpdateValidationTypeDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseValidationTypeDTO:
    repo = ValidationTypeRepository(session)
    service = ValidationTypeService(repo)
    return service.update(id_validation, dto)


@router.delete("/{id_validation}")
def delete_validation_type(
    id_validation: int,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
):
    repo = ValidationTypeRepository(session)
    service = ValidationTypeService(repo)
    return service.delete(id_validation)
