from dto.role_dto import (
    CreateRoleDTO,
    UpdateRoleDTO,
    ResponseRoleDTO,
)
from models.role import Role
from services.base_crud_service import BaseCrudService


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

        role = self.repository.update(
            id_role,
            **data,
        )

        return ResponseRoleDTO.from_entity(role)