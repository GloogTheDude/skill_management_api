from dto.access_level_dto import (
    CreateAccessLevelDTO,
    UpdateAccessLevelDTO,
    ResponseAccessLevelDTO,
)
from models.access_level import AccessLevel
from services.base_crud_service import BaseCrudService


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
        )

        created = self.repository.add(access_level)

        return ResponseAccessLevelDTO.from_entity(created)

    def update(
        self,
        id_access_level: int,
        dto: UpdateAccessLevelDTO,
    ) -> ResponseAccessLevelDTO:

        data = dto.model_dump(exclude_unset=True)

        access_level = self.repository.update(
            id_access_level,
            **data,
        )

        return ResponseAccessLevelDTO.from_entity(access_level)