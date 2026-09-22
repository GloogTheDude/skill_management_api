from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.diploma_skill_repository import DiplomaSkillRepository
from dto.diploma_skill_dto import (
    CreateDiplomaSkillDTO,
    UpdateDiplomaSkillDTO,
    ResponseDiplomaSkillDTO,
)
from services.diploma_skill_service import DiplomaSkillService


router = APIRouter(
    prefix="/diploma_skill",
    tags=["diploma_skill"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_diploma_skill(
    dto: CreateDiplomaSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseDiplomaSkillDTO:

    repo = DiplomaSkillRepository(session)
    service = DiplomaSkillService(repo)

    return service.create(dto)


@router.get("/{id_diploma}/{id_skill}")
def get_diploma_skill_by_ids(
    id_diploma: int,
    id_skill: int,
    session: Session = Depends(get_session),
) -> ResponseDiplomaSkillDTO:

    repo = DiplomaSkillRepository(session)
    service = DiplomaSkillService(repo)

    return service.get_by_id(id_diploma, id_skill)


@router.get("")
def get_diploma_skills(
    session: Session = Depends(get_session),
) -> list[ResponseDiplomaSkillDTO]:

    repo = DiplomaSkillRepository(session)
    service = DiplomaSkillService(repo)

    return service.get_all()


@router.patch("/{id_diploma}/{id_skill}")
def update_diploma_skill(
    id_diploma: int,
    id_skill: int,
    dto: UpdateDiplomaSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseDiplomaSkillDTO:

    repo = DiplomaSkillRepository(session)
    service = DiplomaSkillService(repo)

    return service.update(
        id_diploma,
        id_skill,
        dto,
    )


@router.delete("/{id_diploma}/{id_skill}")
def delete_diploma_skill(
    id_diploma: int,
    id_skill: int,
    session: Session = Depends(get_session),
):
    repo = DiplomaSkillRepository(session)
    service = DiplomaSkillService(repo)

    return service.delete(
        (id_diploma, id_skill)
    )