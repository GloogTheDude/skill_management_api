from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.skill_validation_repository import SkillValidationRepository
from dto.skill_validation_dto import (
    CreateSkillValidationDTO,
    UpdateSkillValidationDTO,
    ResponseSkillValidationDTO,
)
from services.skill_validation_service import SkillValidationService


router = APIRouter(
    prefix="/skill_validation",
    tags=["skill_validation"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_skill_validation(
    dto: CreateSkillValidationDTO,
    session: Session = Depends(get_session),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.create(dto)


@router.get("/{id_skill_validation}")
def get_skill_validation_by_id(
    id_skill_validation: int,
    session: Session = Depends(get_session),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.get_by_id(id_skill_validation)


@router.get("")
def get_skill_validations(
    session: Session = Depends(get_session),
) -> list[ResponseSkillValidationDTO]:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.get_all()


@router.patch("/{id_skill_validation}")
def update_skill_validation(
    id_skill_validation: int,
    dto: UpdateSkillValidationDTO,
    session: Session = Depends(get_session),
) -> ResponseSkillValidationDTO:
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.update(id_skill_validation, dto)


@router.delete("/{id_skill_validation}")
def delete_skill_validation(
    id_skill_validation: int,
    session: Session = Depends(get_session),
):
    repo = SkillValidationRepository(session)
    service = SkillValidationService(repo)
    return service.delete(id_skill_validation)
