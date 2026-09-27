from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.domaine_repository import DomaineRepository
from dto.domaine_dto import (
    CreateDomaineDTO,
    UpdateDomaineDTO,
    ResponseDomaineDTO,
)
from services.domaine_service import DomaineService
from controlers.auth_controller import get_current_employee, require_hr_employee
from errors.authorization_errors import AuthorizationForbidden


router = APIRouter(prefix="/domaine", tags=["domaine"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_domaine(
    dto: CreateDomaineDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseDomaineDTO:
    repo = DomaineRepository(session)
    service = DomaineService(repo)
    return service.create(dto)


@router.get("/{id_domaine}")
def get_domaine_by_id(
    id_domaine: int,
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> ResponseDomaineDTO:
    repo = DomaineRepository(session)
    service = DomaineService(repo)
    return service.get_by_id(id_domaine)


@router.get("")
def get_domaines(
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> list[ResponseDomaineDTO]:
    repo = DomaineRepository(session)
    service = DomaineService(repo)
    return service.get_all()


@router.patch("/{id_domaine}")
def update_domaine(
    id_domaine: int,
    dto: UpdateDomaineDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseDomaineDTO:
    repo = DomaineRepository(session)
    service = DomaineService(repo)
    return service.update(id_domaine, dto)


@router.delete("/{id_domaine}")
def delete_domaine(
    id_domaine: int,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
):
    repo = DomaineRepository(session)
    service = DomaineService(repo)
    return service.delete(id_domaine)
