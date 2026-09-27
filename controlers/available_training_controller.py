from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from dto.available_training_dto import AvailableTrainingDTO
from services.available_training_service import AvailableTrainingService


router = APIRouter(tags=["trainings"])


@router.get(
    "/employees/{id_employee}/available-trainings",
    response_model=list[AvailableTrainingDTO],
)
def get_available_trainings(
    id_employee: int,
    id_domaine: int | None = Query(default=None, gt=0),
    session: Session = Depends(get_session),
) -> list[AvailableTrainingDTO]:
    service = AvailableTrainingService(
        EmployeeRepository(session),
        TrainingRepository(session),
    )
    return service.get_available_trainings(id_employee, id_domaine)
