from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from dto.available_training_dto import AvailableTrainingDTO
from services.available_training_service import AvailableTrainingService
from controlers.auth_controller import get_current_employee
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from sqlalchemy.exc import NoResultFound


router = APIRouter(tags=["trainings"])


@router.get(
    "/employees/{id_employee}/available-trainings",
    response_model=list[AvailableTrainingDTO],
)
def get_available_trainings(
    id_employee: int,
    id_domaine: int | None = Query(default=None, gt=0),
    session: Session = Depends(get_session),
    current_employee: AuthEmployeeDTO = Depends(get_current_employee),
) -> list[AvailableTrainingDTO]:
    service = AvailableTrainingService(
        EmployeeRepository(session),
        TrainingRepository(session),
    )
    try:
        return service.get_available_trainings(id_employee, id_domaine, current_employee)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Employee not found.") from exc
    except AuthorizationForbidden as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
