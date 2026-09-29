from datetime import date

import pytest
from types import SimpleNamespace
from pydantic import ValidationError

from dto.skill_validation_dto import (
    CreateSkillValidationDTO,
    UpdateSkillValidationDTO,
)
from services.skill_validation_service import SkillValidationService
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from services.employee_authorization_service import EmployeeAuthorizationService


class FakeSkillValidationRepository:
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
        entity.id_skill_validation = self.next_id
        self.next_id += 1
        self.entities[entity.id_skill_validation] = entity
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


@pytest.mark.parametrize(
    "field",
    [
        "id_validation",
        "id_employee",
        "id_skill",
    ],
)
def test_update_skill_validation_rejects_null_foreign_key(field):
    with pytest.raises(ValidationError):
        UpdateSkillValidationDTO(**{field: None})


def test_update_skill_validation_omitted_fields_are_not_in_dump():
    dto = UpdateSkillValidationDTO()

    assert dto.model_dump(exclude_unset=True) == {}


def test_update_skill_validation_accepts_positive_foreign_key():
    dto = UpdateSkillValidationDTO(id_skill=12)

    assert dto.id_skill == 12
    assert dto.model_dump(exclude_unset=True) == {
        "id_skill": 12,
    }


def test_update_skill_validation_allows_nullable_fields_to_be_null():
    dto = UpdateSkillValidationDTO(
        date_=None,
        level_skill=None,
    )

    assert dto.model_dump(exclude_unset=True) == {
        "date_": None,
        "level_skill": None,
    }


def test_skill_validation_crud_and_partial_update():
    repository = FakeSkillValidationRepository()
    service = SkillValidationService(repository)

    created = service.create(
        CreateSkillValidationDTO(
            date_=date(2026, 9, 25),
            level_skill=None,
            id_validation=1,
                id_employee=2,
                id_skill=4,
            ),
            validator_id=3,
        )

    assert created.id_skill_validation == 1
    assert created.id_validation == 1
    assert created.id_employee == 2
    assert created.id_validator == 3
    assert created.id_skill == 4
    assert service.get_all()[0].date_ == date.today()

    with pytest.raises(ValueError):
        service.update(1, UpdateSkillValidationDTO(id_skill=5))

    updated = service.update(1, UpdateSkillValidationDTO(level_skill=4))
    assert updated.level_skill == 4
    assert updated.id_employee == 2
    assert updated.id_validator == 3

    unchanged = service.update(
        1,
        UpdateSkillValidationDTO(),
    )

    assert unchanged.id_skill == 4
    assert unchanged.id_employee == 2
    assert unchanged.id_validator == 3

    deleted = service.delete(1)

    assert deleted.is_deleted is True
    assert service.get_all() == []


def _actor(employee_id: int, access_level: int) -> AuthEmployeeDTO:
    return AuthEmployeeDTO(
        id_employee=employee_id,
        first_name="Test",
        last_name="User",
        mail="test@example.com",
        role_name=None,
        access_level_label=None,
        access_level=access_level,
    )


@pytest.mark.parametrize(
    ("actor", "target", "allowed"),
    [
        (_actor(1, 1), SimpleNamespace(id_employee=1, id_manager=None), False),
        (_actor(2, 2), SimpleNamespace(id_employee=3, id_manager=2), True),
        (_actor(2, 2), SimpleNamespace(id_employee=2, id_manager=None), False),
        (_actor(2, 2), SimpleNamespace(id_employee=4, id_manager=9), False),
        (_actor(3, 3), SimpleNamespace(id_employee=99, id_manager=42), True),
    ],
)
def test_skill_validation_creation_scope(actor, target, allowed):
    if allowed:
        EmployeeAuthorizationService.authorize_action(actor, target)
    else:
        with pytest.raises(AuthorizationForbidden):
            EmployeeAuthorizationService.authorize_action(actor, target)


def test_skill_validation_input_does_not_accept_validator():
    assert "id_validator" not in CreateSkillValidationDTO.model_fields
    assert "id_validator" not in UpdateSkillValidationDTO.model_fields
