from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.training_repository import TrainingRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_source_repository import TrainingSourceRepository
from dto.training_dto import (
    CreateTrainingDTO,
    UpdateTrainingDTO,
    ResponseTrainingDTO,
)
from services.training_service import TrainingService
from controlers.auth_controller import get_current_employee, require_hr_employee
from dto.skill_link_replacement_dto import ReplaceTrainingSkillsDTO
from dto.training_skill_dto import ResponseTrainingSkillDTO
from services.training_support_service import TrainingSupportService


router = APIRouter(prefix="/training", tags=["training"])


@router.put("s/{id_training}/skills", response_model=list[ResponseTrainingSkillDTO])
def replace_training_skills(id_training: int, dto: ReplaceTrainingSkillsDTO,
                            session: Session = Depends(get_session),
                            _: object = Depends(require_hr_employee)):
    try:
        links = TrainingSupportService(session).replace_skills(
            id_training,
            [(item.id_skill, item.level) for item in dto.skills],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return [ResponseTrainingSkillDTO.from_entity(link) for link in links]

@router.post('',status_code=201)
def create_training(dto:CreateTrainingDTO,
                    session:Session=Depends(get_session),
                    _: object = Depends(require_hr_employee))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo, DomaineRepository(session), TrainingSourceRepository(session))
    try:
        return service.create(dto)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get('/{id_training}')
def get_training_by_id(id_training:int,
                       session:Session=Depends(get_session),
                       _: object = Depends(get_current_employee))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo, DomaineRepository(session), TrainingSourceRepository(session))
    return service.get_by_id(id_training)

@router.get('')
def get_trainings(session:Session=Depends(get_session),
                  _: object = Depends(get_current_employee))->list[ResponseTrainingDTO]:
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.get_all()

@router.patch(
    "/{id_training}",
    response_model=ResponseTrainingDTO
)
def update_training(id_training:int, 
                    dto:UpdateTrainingDTO,
                    session:Session=Depends(get_session),
                    _: object = Depends(require_hr_employee))->ResponseTrainingDTO:
    repo = TrainingRepository(session)
    service = TrainingService(repo, DomaineRepository(session), TrainingSourceRepository(session))
    try:
        return service.update(id_training, dto)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.delete('/{id_training}')
def delete_training(id_training:int,
                    session: Session=Depends(get_session),
                    _: object = Depends(require_hr_employee)):
    repo = TrainingRepository(session)
    service = TrainingService(repo)
    return service.delete(id_training)
