from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_skill_repository import TrainingSkillRepository
from dto.training_skill_dto import CreateTrainingSkillDTO, UpdateTrainingSkillDTO, ResponseTrainingSkillDTO
from services.training_skill_service import TrainingSkillService
from controlers.auth_controller import get_current_employee, require_hr_employee
router = APIRouter(
    prefix="/training_skill",
    tags=["training_skill"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_training_skill(
    dto:CreateTrainingSkillDTO,
    session:Session=Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)-> ResponseTrainingSkillDTO:
    repo = TrainingSkillRepository(session)
    service = TrainingSkillService(repo)
    return service.create(dto)

@router.get("/{id_skill}/{id_training}")
def get_training_skill_by_ids(
    id_training:int,
    id_skill: int,
    session: Session = Depends(get_session)
    ,_: object = Depends(get_current_employee)
)->ResponseTrainingSkillDTO:
    repo = TrainingSkillRepository(session)
    service = TrainingSkillService(repo)
    return service.get_by_id(id_training, id_skill)


@router.get("")
def get_training_skills(
    session: Session = Depends(get_session)
    ,_: object = Depends(get_current_employee)
)->list[ResponseTrainingSkillDTO]:
    repo = TrainingSkillRepository(session)
    service = TrainingSkillService(repo)
    return service.get_all()


@router.patch("/{id_training}/{id_skill}")
def update_training_skill(
    id_training:int,
    id_skill: int,
    dto:UpdateTrainingSkillDTO,
    session: Session = Depends(get_session)
    ,_: object = Depends(require_hr_employee)
)->ResponseTrainingSkillDTO:
    repo = TrainingSkillRepository(session)
    service = TrainingSkillService(repo)
    return service.update(id_training, id_skill, dto)

@router.delete("/{id_training}/{id_skill}")
def delete_training_skill(
    id_training:int,
    id_skill: int,
    session: Session = Depends(get_session)
    ,_: object = Depends(require_hr_employee)
):
    repo = TrainingSkillRepository(session)
    service = TrainingSkillService(repo)
    return service.delete((id_skill, id_training))
