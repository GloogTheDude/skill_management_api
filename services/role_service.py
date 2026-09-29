from dto.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    ResponseRoleDTO,
)
from models.role import Role
from services.base_crud_service import BaseCrudService
from services.administrative_security_service import AdministrativeSecurityService
from models.access_level import AccessLevel
from core.constants import PermissionProfile


class RoleService(BaseCrudService[Role]):

    def get_all(self) -> list[ResponseRoleDTO]:
        roles = self._get_all_entities()

        return [
            ResponseRoleDTO.from_entity(role)
            for role in roles
        ]

    def get_by_id(
        self,
        id_role: int,
    ) -> ResponseRoleDTO:

        role = self._get_entity_by_id(id_role)

        return ResponseRoleDTO.from_entity(role)

    def create(
        self,
        dto: CreateRoleDTO,
    ) -> ResponseRoleDTO:

        role = Role(
            denomination_role=dto.denomination_role,
            id_access_level=dto.id_access_level,
        )

        created = self.repository.add(role)

        return ResponseRoleDTO.from_entity(created)

    def update(
        self,
        id_role: int,
        dto: UpdateRoleDTO,
    ) -> ResponseRoleDTO:

        data = dto.model_dump(exclude_unset=True)
        current = self.repository.get_one(id_role)
        next_access_level = current.id_access_level
        if "id_access_level" in data:
            next_access_level = data["id_access_level"]
        target = self.repository._session.get(AccessLevel, next_access_level)
        if current.access_level.permission_profile == PermissionProfile.HR.value and (
            target is None or target.permission_profile != PermissionProfile.HR.value
        ):
            AdministrativeSecurityService.ensure_hr_survives(
                self.repository._session,
                AdministrativeSecurityService.employees_for_role(self.repository._session, id_role),
            )

        role = self.repository.update(
            id_role,
            **data,
        )

        return ResponseRoleDTO.from_entity(role)

    def delete(self, id_role: int):
        current = self.repository.get_one(id_role)
        if current.access_level.permission_profile == PermissionProfile.HR.value:
            AdministrativeSecurityService.ensure_hr_survives(
                self.repository._session,
                AdministrativeSecurityService.employees_for_role(self.repository._session, id_role),
            )
        return super().delete(id_role)
