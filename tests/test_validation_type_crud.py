from dto.validation_type_dto import (
    CreateValidationTypeDTO,
    UpdateValidationTypeDTO,
)
from services.validation_type_service import ValidationTypeService


class FakeValidationTypeRepository:
    def __init__(self):
        self.entities = {}
        self.next_id = 1

    def get_all(self):
        return [
            entity
            for entity in self.entities.values()
            if not entity.is_deleted
        ]

    def get_one(self, ident):
        return self.entities[ident]

    def add(self, entity):
        entity.id_validation = self.next_id
        self.next_id += 1
        self.entities[entity.id_validation] = entity
        return entity

    def update(self, ident, **kwargs):
        entity = self.entities[ident]
        for field, value in kwargs.items():
            setattr(entity, field, value)
        return entity

    def soft_delete(self, ident):
        entity = self.entities[ident]
        entity.is_deleted = True
        return entity


def test_validation_type_crud_and_partial_update():
    repository = FakeValidationTypeRepository()
    service = ValidationTypeService(repository)

    created = service.create(
        CreateValidationTypeDTO(
            source="manual",
            denomination_validation="Manager validation",
        )
    )

    assert created.id_validation == 1
    assert created.source == "manual"
    assert service.get_all()[0].denomination_validation == "Manager validation"

    updated = service.update(
        1,
        UpdateValidationTypeDTO(source=None),
    )

    assert updated.source is None
    assert updated.denomination_validation == "Manager validation"

    unchanged = service.update(
        1,
        UpdateValidationTypeDTO(),
    )

    assert unchanged.source is None
    assert unchanged.denomination_validation == "Manager validation"

    deleted = service.delete(1)

    assert deleted.is_deleted is True
    assert service.get_all() == []
