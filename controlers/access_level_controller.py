from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.access_level_repository import AccessLevelRepository
from dto.access_level_dto import (
    CreateAccessLevelDTO,
    UpdateAccessLevelDTO,
    ResponseAccessLevelDTO,
)
from services.access_level_service import AccessLevelService


router = APIRouter(
    prefix="/access_level",
    tags=["access_level"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_access_level(
    dto: CreateAccessLevelDTO,
    session: Session = Depends(get_session),
) -> ResponseAccessLevelDTO:

    repo = AccessLevelRepository(session)
    service = AccessLevelService(repo)

    return service.create(dto)


@router.get("/{id_access_level}")
def get_access_level_by_id(
    id_access_level: int,
    session: Session = Depends(get_session),
) -> ResponseAccessLevelDTO:

    repo = AccessLevelRepository(session)
    service = AccessLevelService(repo)

    return service.get_by_id(id_access_level)


@router.get("")
def get_access_levels(
    session: Session = Depends(get_session),
) -> list[ResponseAccessLevelDTO]:

    repo = AccessLevelRepository(session)
    service = AccessLevelService(repo)

    return service.get_all()


@router.patch("/{id_access_level}")
def update_access_level(
    id_access_level: int,
    dto: UpdateAccessLevelDTO,
    session: Session = Depends(get_session),
) -> ResponseAccessLevelDTO:

    repo = AccessLevelRepository(session)
    service = AccessLevelService(repo)

    return service.update(
        id_access_level,
        dto,
    )


@router.delete("/{id_access_level}")
def delete_access_level(
    id_access_level: int,
    session: Session = Depends(get_session),
):
    repo = AccessLevelRepository(session)
    service = AccessLevelService(repo)

    return service.delete(id_access_level)