from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.auth_controller import get_current_employee
from core.database import get_session
from dto.auth_dto import AuthEmployeeDTO
from dto.dashboard_dto import DashboardDTO
from services.dashboard_service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardDTO)
def get_dashboard(
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> DashboardDTO:
    return DashboardService(session).get_dashboard(current_employee)
