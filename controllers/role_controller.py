from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_session
from db.repositories.role_repository import RoleRepository
from dto.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    ResponseRoleDTO,
)
from services.role_service import RoleService
from controllers.auth_controller import get_current_employee, require_hr_employee


router = APIRouter(
    prefix="/role",
    tags=["role"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_role(
    dto: CreateRoleDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseRoleDTO:

    repo = RoleRepository(session)
    service = RoleService(repo)

    return service.create(dto)


@router.get("/{id_role}")
def get_role_by_id(
    id_role: int,
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> ResponseRoleDTO:

    repo = RoleRepository(session)
    service = RoleService(repo)

    return service.get_by_id(id_role)


@router.get("")
def get_roles(
    session: Session = Depends(get_session),
    _: object = Depends(get_current_employee),
) -> list[ResponseRoleDTO]:

    repo = RoleRepository(session)
    service = RoleService(repo)

    return service.get_all()


@router.patch("/{id_role}")
def update_role(
    id_role: int,
    dto: UpdateRoleDTO,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
) -> ResponseRoleDTO:

    repo = RoleRepository(session)
    service = RoleService(repo)

    return service.update(id_role, dto)


@router.delete("/{id_role}")
def delete_role(
    id_role: int,
    session: Session = Depends(get_session),
    _: object = Depends(require_hr_employee),
):
    repo = RoleRepository(session)
    service = RoleService(repo)

    return service.delete(id_role)
