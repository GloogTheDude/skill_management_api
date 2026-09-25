from dto.validation_type_dto import (
    CreateValidationTypeDTO,
    UpdateValidationTypeDTO,
    ResponseValidationTypeDTO,
)
from models.validation_type import ValidationType
from services.base_crud_service import BaseCrudService


class ValidationTypeService(BaseCrudService[ValidationType]):

    def get_all(self) -> list[ResponseValidationTypeDTO]:
        validation_types = self._get_all_entities()

        return [
            ResponseValidationTypeDTO.from_entity(validation_type)
            for validation_type in validation_types
        ]

    def get_by_id(
        self,
        id_validation: int,
    ) -> ResponseValidationTypeDTO:
        validation_type = self._get_entity_by_id(id_validation)
        return ResponseValidationTypeDTO.from_entity(validation_type)

    def create(
        self,
        dto: CreateValidationTypeDTO,
    ) -> ResponseValidationTypeDTO:
        validation_type = ValidationType(
            source=dto.source,
            denomination_validation=dto.denomination_validation,
        )

        created = self.repository.add(validation_type)
        return ResponseValidationTypeDTO.from_entity(created)

    def update(
        self,
        id_validation: int,
        dto: UpdateValidationTypeDTO,
    ) -> ResponseValidationTypeDTO:
        data = dto.model_dump(exclude_unset=True)

        validation_type = self.repository.update(
            id_validation,
            **data,
        )

        return ResponseValidationTypeDTO.from_entity(validation_type)
