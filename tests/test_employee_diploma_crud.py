from datetime import date

from dto.employee_diploma_dto import (
    CreateEmployeeDiplomaDTO,
    UpdateEmployeeDiplomaDTO,
)
from models.employee_diploma import EmployeeDiploma
from services.employee_diploma_service import EmployeeDiplomaService


class FakeEmployeeDiplomaRepository:
    def __init__(self):
        self.entities: dict[tuple[int, int], EmployeeDiploma] = {}

    def get_all(self):
        return [
            entity
            for entity in self.entities.values()
            if not entity.is_deleted
        ]

    def get_one(self, ident):
        return self.entities[ident]

    def add(self, entity):
        self.entities[(entity.id_employee, entity.id_diploma)] = entity
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


def test_create_dto_requires_positive_composite_key():
    dto = CreateEmployeeDiplomaDTO(id_employee=3, id_diploma=7)

    assert dto.id_employee == 3
    assert dto.id_diploma == 7


def test_create_dto_rejects_non_positive_composite_key():
    for field in ("id_employee", "id_diploma"):
        values = {"id_employee": 3, "id_diploma": 7}
        values[field] = 0

        try:
            CreateEmployeeDiplomaDTO(**values)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{field} should be positive")


def test_update_dto_does_not_contain_composite_key_fields():
    dto = UpdateEmployeeDiplomaDTO(school="University")

    assert dto.model_dump(exclude_unset=True) == {"school": "University"}
    assert not hasattr(dto, "id_employee")
    assert not hasattr(dto, "id_diploma")


def test_update_dto_empty_does_not_set_fields():
    assert UpdateEmployeeDiplomaDTO().model_dump(exclude_unset=True) == {}


def test_update_dto_accepts_explicit_null_for_nullable_fields():
    dto = UpdateEmployeeDiplomaDTO(school=None, start_=None)

    assert dto.model_dump(exclude_unset=True) == {
        "school": None,
        "start_": None,
    }


def test_crud_service_handles_composite_key_and_soft_delete():
    repository = FakeEmployeeDiplomaRepository()
    service = EmployeeDiplomaService(repository)

    created = service.create(
        CreateEmployeeDiplomaDTO(
            id_employee=3,
            id_diploma=7,
            start_=date(2020, 9, 1),
            school="University",
            distinction="Great",
        )
    )

    assert created.id_employee == 3
    assert created.id_diploma == 7
    assert created.start_ == date(2020, 9, 1)

    updated = service.update(
        3,
        7,
        UpdateEmployeeDiplomaDTO(end_=date(2024, 6, 30)),
    )
    assert updated.end_ == date(2024, 6, 30)
    assert updated.school == "University"

    unchanged = service.update(3, 7, UpdateEmployeeDiplomaDTO())
    assert unchanged.school == "University"
    assert unchanged.end_ == date(2024, 6, 30)

    service.delete((3, 7))
    assert service.get_all() == []


def test_legacy_add_keeps_completion_workflow_compatible():
    repository = FakeEmployeeDiplomaRepository()
    service = EmployeeDiplomaService(repository)

    created = service.add(
        employee_id=3,
        diploma_id=7,
        start_=date(2020, 9, 1),
        end_=date(2024, 6, 30),
        distinction="Great",
        school="University",
    )

    assert created.id_employee == 3
    assert created.id_diploma == 7
    assert created.doc is None
    assert created.is_deleted is False
