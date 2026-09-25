from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from dto.employee_certification_crud_dto import (
    CreateEmployeeCertificationDTO,
    ResponseEmployeeCertificationDTO,
    UpdateEmployeeCertificationDTO,
)
from services.employee_certification_service import EmployeeCertificationService


router = APIRouter(
    prefix="/employee_certification",
    tags=["employee_certification"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employee_certification(
    dto: CreateEmployeeCertificationDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.create(dto)


@router.get("/{id_employee_certification}")
def get_employee_certification_by_id(
    id_employee_certification: int,
    session: Session = Depends(get_session),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.get_by_id(id_employee_certification)


@router.get("")
def get_employee_certifications(
    session: Session = Depends(get_session),
) -> list[ResponseEmployeeCertificationDTO]:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.get_all()


@router.patch("/{id_employee_certification}")
def update_employee_certification(
    id_employee_certification: int,
    dto: UpdateEmployeeCertificationDTO,
    session: Session = Depends(get_session),
) -> ResponseEmployeeCertificationDTO:
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.update(id_employee_certification, dto)


@router.delete("/{id_employee_certification}")
def delete_employee_certification(
    id_employee_certification: int,
    session: Session = Depends(get_session),
):
    repo = EmployeeCertificationRepository(session)
    service = EmployeeCertificationService(repo)
    return service.delete(id_employee_certification)
