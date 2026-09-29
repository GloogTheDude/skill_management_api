from dto.access_level_dto import (
    CreateAccessLevelDTO,
    UpdateAccessLevelDTO,
    ResponseAccessLevelDTO,
)
from models.access_level import AccessLevel
from services.base_crud_service import BaseCrudService
from services.administrative_security_service import AdministrativeSecurityService
from core.constants import PermissionProfile


class AccessLevelService(BaseCrudService[AccessLevel]):

    def get_all(self) -> list[ResponseAccessLevelDTO]:
        access_levels = self._get_all_entities()

        return [
            ResponseAccessLevelDTO.from_entity(access_level)
            for access_level in access_levels
        ]

    def get_by_id(
        self,
        id_access_level: int,
    ) -> ResponseAccessLevelDTO:

        access_level = self._get_entity_by_id(id_access_level)

        return ResponseAccessLevelDTO.from_entity(access_level)

    def create(
        self,
        dto: CreateAccessLevelDTO,
    ) -> ResponseAccessLevelDTO:

        access_level = AccessLevel(
            label=dto.label,
            level=dto.level,
            permission_profile=dto.permission_profile.value,
        )

        created = self.repository.add(access_level)

        return ResponseAccessLevelDTO.from_entity(created)

    def update(
        self,
        id_access_level: int,
        dto: UpdateAccessLevelDTO,
    ) -> ResponseAccessLevelDTO:

        data = dto.model_dump(exclude_unset=True)

        current = self.repository.get_one(id_access_level)
        next_profile = data.get("permission_profile", current.permission_profile)
        if isinstance(next_profile, PermissionProfile):
            next_profile = next_profile.value
        if current.permission_profile == PermissionProfile.HR.value and next_profile != PermissionProfile.HR.value:
            AdministrativeSecurityService.ensure_hr_survives(
                self.repository._session,
                AdministrativeSecurityService.employees_for_access_level(self.repository._session, id_access_level),
            )

        access_level = self.repository.update(
            id_access_level,
            **data,
        )

        return ResponseAccessLevelDTO.from_entity(access_level)

    def delete(self, id_access_level: int):
        current = self.repository.get_one(id_access_level)
        if current.permission_profile == PermissionProfile.HR.value:
            AdministrativeSecurityService.ensure_hr_survives(
                self.repository._session,
                AdministrativeSecurityService.employees_for_access_level(self.repository._session, id_access_level),
            )
        return super().delete(id_access_level)
