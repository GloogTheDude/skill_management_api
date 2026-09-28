from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from dto.employee_certification_expiration_dto import (
    EmployeeCertificationExpirationDTO,
)
from services.employee_certification_service import EmployeeCertificationService
from controllers.auth_controller import require_hr_employee
from dto.auth_dto import AuthEmployeeDTO


router = APIRouter(tags=["employee certifications"])


@router.get(
    "/employee-certifications/expiring",
    response_model=list[EmployeeCertificationExpirationDTO],
)
def get_expiring_employee_certifications(
    session: Session = Depends(get_session),
    _: AuthEmployeeDTO = Depends(require_hr_employee),
) -> list[EmployeeCertificationExpirationDTO]:
    service = EmployeeCertificationService(EmployeeCertificationRepository(session))
    return service.get_expiring()
