from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.certification_skill_repository import CertificationSkillRepository
from dto.certification_skill_dto import (
    CreateCertificationSkillDTO,
    UpdateCertificationSkillDTO,
    ResponseCertificationSkillDTO,
)
from services.certification_skill_service import CertificationSkillService


router = APIRouter(
    prefix="/certification_skill",
    tags=["certification_skill"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_certification_skill(
    dto: CreateCertificationSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseCertificationSkillDTO:

    repo = CertificationSkillRepository(session)
    service = CertificationSkillService(repo)

    return service.create(dto)


@router.get("/{id_certification}/{id_skill}")
def get_certification_skill_by_ids(
    id_certification: int,
    id_skill: int,
    session: Session = Depends(get_session),
) -> ResponseCertificationSkillDTO:

    repo = CertificationSkillRepository(session)
    service = CertificationSkillService(repo)

    return service.get_by_id(id_certification, id_skill)


@router.get("")
def get_certification_skills(
    session: Session = Depends(get_session),
) -> list[ResponseCertificationSkillDTO]:

    repo = CertificationSkillRepository(session)
    service = CertificationSkillService(repo)

    return service.get_all()


@router.patch("/{id_certification}/{id_skill}")
def update_certification_skill(
    id_certification: int,
    id_skill: int,
    dto: UpdateCertificationSkillDTO,
    session: Session = Depends(get_session),
) -> ResponseCertificationSkillDTO:

    repo = CertificationSkillRepository(session)
    service = CertificationSkillService(repo)

    return service.update(
        id_certification,
        id_skill,
        dto,
    )


@router.delete("/{id_certification}/{id_skill}")
def delete_certification_skill(
    id_certification: int,
    id_skill: int,
    session: Session = Depends(get_session),
):
    repo = CertificationSkillRepository(session)
    service = CertificationSkillService(repo)

    return service.delete(
        (id_certification, id_skill)
    )