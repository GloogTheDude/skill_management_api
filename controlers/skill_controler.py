from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.skills_repository import SkillRepository
from dto.skill_dto import (
    CreateSkillDTO,
    UpdateSkillDTO,
    ResponseSkillDTO,
)
from services.skill_service import SkillService


router = APIRouter(prefix="/skill", tags=["skill"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_skill(
    dto: CreateSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseSkillDTO:
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.create(dto)


@router.get("/{id_skill}")
def get_skill_by_id(
    id_skill: int,
    session: Session = Depends(get_session),
) -> ResponseSkillDTO:
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.get_by_id(id_skill)


@router.get("")
def get_all_skills(
    session: Session = Depends(get_session),
) -> list[ResponseSkillDTO]:
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.get_all()


@router.patch("/{id_skill}")
def update_skill(
    id_skill: int,
    dto: UpdateSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseSkillDTO:
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.update(id_skill, dto)


@router.delete("/{id_skill}")
def delete_skill(
    id_skill: int,
    session: Session = Depends(get_session),
):
    repo = SkillRepository(session)
    service = SkillService(repo)
    return service.delete(id_skill)