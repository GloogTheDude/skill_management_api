from datetime import date

import pytest
from pydantic import ValidationError

from dto.employee_certification_crud_dto import (
    CreateEmployeeCertificationDTO,
    UpdateEmployeeCertificationDTO,
)
from models.employee_certification import EmployeeCertification
from services.employee_certification_service import EmployeeCertificationService


class FakeEmployeeCertificationRepository:
    def __init__(self):
        self.entities: dict[int, EmployeeCertification] = {}
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
        if entity.id_employee_certification is None:
            entity.id_employee_certification = self.next_id
            self.next_id += 1
        self.entities[entity.id_employee_certification] = entity
        return entity

    def update(self, ident, **kwargs):
        entity = self.get_one(ident)
        for field, value in kwargs.items():
            setattr(entity, field, value)
        return entity

    def soft_delete(self, ident):
        entity = self.get_one(ident)
        entity.is_deleted = True
        return entity

@pytest.mark.parametrize("field", ["id_employee", "id_certification"])
def test_update_dto_rejects_explicit_null_foreign_keys(field):
    with pytest.raises(ValidationError):
        UpdateEmployeeCertificationDTO(**{field: None})


def test_update_dto_omitted_foreign_keys_are_not_dumped():
    dto = UpdateEmployeeCertificationDTO(organism="Company")

    assert dto.model_dump(exclude_unset=True) == {"organism": "Company"}


def test_update_dto_accepts_positive_foreign_keys():
    dto = UpdateEmployeeCertificationDTO(id_employee=4, id_certification=8)

    assert dto.model_dump(exclude_unset=True) == {
        "id_employee": 4,
        "id_certification": 8,
    }


def test_update_dto_empty_does_not_set_fields():
    assert UpdateEmployeeCertificationDTO().model_dump(exclude_unset=True) == {}


def test_crud_service_handles_update_and_soft_delete():
    repository = FakeEmployeeCertificationRepository()
    service = EmployeeCertificationService(repository)

    created = service.create(
        CreateEmployeeCertificationDTO(
            id_employee=4,
            id_certification=8,
            start_=date(2024, 1, 1),
            organism="Company",
            evaluation="Passed",
        )
    )

    assert created.id_employee_certification == 1
    assert created.id_employee == 4

    updated = service.update(
        1,
        UpdateEmployeeCertificationDTO(
            id_employee=5,
            expiration=date(2026, 1, 1),
        ),
    )
    assert updated.id_employee == 5
    assert updated.id_certification == 8
    assert updated.organism == "Company"

    unchanged = service.update(1, UpdateEmployeeCertificationDTO())
    assert unchanged.expiration == date(2026, 1, 1)

    service.delete(1)
    assert service.get_all() == []
