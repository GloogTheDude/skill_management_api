from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import NoResultFound

from dto.employee_dto import CreateEmployeeDTO, UpdateEmployeeDTO
from dto.training_dto import CreateTrainingDTO, UpdateTrainingDTO
from services.employee_service import EmployeeService
from services.training_service import TrainingService
from models.employee import Employee
from models.training import Training
from models.role import Role
from models.domaine import Domaine
from models.training_source import TrainingSource


class FakeRepository:
    def __init__(self, entity=None):
        self.entity = entity

    def get_one(self, ident):
        if self.entity is None or getattr(self.entity, "id_employee", getattr(self.entity, "id_training", None)) != ident:
            raise NoResultFound()
        return self.entity

    def add(self, entity):
        if isinstance(entity, Employee):
            entity.id_employee = 1
        if isinstance(entity, Employee) and entity.role is None:
            entity.role = Role(denomination_role="Employee", id_access_level=1)
        if isinstance(entity, Training):
            entity.id_training = 10
            entity.domaine = Domaine(nom_domaine="Backend")
            entity.source = TrainingSource(name_source="Internal")
        self.entity = entity
        return entity

    def update(self, ident, **kwargs):
        entity = self.get_one(ident)
        for key, value in kwargs.items():
            setattr(entity, key, value)
        return entity


class FakeRelatedRepository:
    def __init__(self, entities):
        self.entities = entities

    def get_one(self, ident):
        if ident not in self.entities:
            raise NoResultFound()
        return self.entities[ident]


def related(active=True):
    return SimpleNamespace(is_deleted=not active)


def training_dto(**overrides):
    values = {
        "title": "Python",
        "id_domaine": 1,
        "id_source": 1,
        "id_diploma": 1,
        "start_": date(2030, 1, 1),
        "end_": date(2030, 1, 2),
        "cost_hour": Decimal("10"),
        "duration_hours": Decimal("2"),
    }
    values.update(overrides)
    return CreateTrainingDTO(**values)


def test_employee_create_rejects_missing_or_deleted_role():
    repository = FakeRepository()
    roles = FakeRelatedRepository({1: related(), 2: related(active=False)})
    service = EmployeeService(repository, roles)

    dto = CreateEmployeeDTO(password="secret", id_role=1)
    created = service.create(dto)
    assert created.id_role == 1

    with pytest.raises(NoResultFound):
        service.create(dto.model_copy(update={"id_role": 2}))
    with pytest.raises(NoResultFound):
        service.create(dto.model_copy(update={"id_role": 3}))


def test_employee_update_rejects_self_manager():
    employee = Employee(
        id_employee=7,
        id_role=1,
        role=Role(denomination_role="Employee", id_access_level=1),
    )
    service = EmployeeService(FakeRepository(employee), FakeRelatedRepository({1: related()}))

    with pytest.raises(ValueError):
        service.update(7, UpdateEmployeeDTO(id_manager=7))

    service.update(7, UpdateEmployeeDTO(id_manager=8))
    service.update(7, UpdateEmployeeDTO(id_manager=None))


def make_training():
    training = Training(
        id_training=10,
        id_domaine=1,
        id_source=1,
        id_diploma=1,
        id_certification=None,
        domaine=Domaine(nom_domaine="Backend"),
        source=TrainingSource(name_source="Internal"),
    )
    return training


def make_training_service(training=None):
    return TrainingService(
        FakeRepository(training),
        FakeRelatedRepository({1: related(), 2: related(active=False)}),
        FakeRelatedRepository({1: related(), 2: related(active=False)}),
    )


def test_training_requires_active_domaine_and_source():
    service = make_training_service()
    service.create(training_dto())

    with pytest.raises(NoResultFound):
        service.create(training_dto(id_domaine=2))
    with pytest.raises(NoResultFound):
        service.create(training_dto(id_domaine=3))
    with pytest.raises(NoResultFound):
        service.create(training_dto(id_source=2))
    with pytest.raises(NoResultFound):
        service.create(training_dto(id_source=3))


def test_training_location_is_created_and_returned_or_null():
    service = make_training_service()

    with_location = service.create(training_dto(location="Sart Tilman — Bâtiment B37"))
    assert with_location.location == "Sart Tilman — Bâtiment B37"

    without_location = service.create(training_dto(location=None))
    assert without_location.location is None


def test_training_location_patch_preserves_absent_and_clears_explicit_null():
    training = make_training()
    training.location = "Sart Tilman — Bâtiment B37"
    service = make_training_service(training)

    service.update(10, UpdateTrainingDTO(title="Python avancé"))
    assert training.location == "Sart Tilman — Bâtiment B37"

    service.update(10, UpdateTrainingDTO(location="Microsoft Teams"))
    assert training.location == "Microsoft Teams"

    service.update(10, UpdateTrainingDTO(location=None))
    assert training.location is None


def test_training_rejects_both_diploma_and_certification():
    service = make_training_service()
    with pytest.raises(ValueError):
        service.create(training_dto(id_diploma=1, id_certification=1))


def test_training_patch_validates_final_target_state_and_allows_switching():
    training = make_training()
    service = make_training_service(training)

    with pytest.raises(ValueError):
        service.update(10, UpdateTrainingDTO(id_certification=2))

    updated = service.update(
        10,
        UpdateTrainingDTO(id_diploma=None, id_certification=2),
    )
    assert training.id_diploma is None
    assert training.id_certification == 2

    training.id_certification = 2
    training.id_diploma = None
    updated = service.update(
        10,
        UpdateTrainingDTO(id_certification=None, id_diploma=1),
    )
    assert training.id_certification is None
    assert training.id_diploma == 1

    training.id_diploma = None
    training.id_certification = 2
    with pytest.raises(ValueError):
        service.update(10, UpdateTrainingDTO(id_diploma=1))

    service.update(10, UpdateTrainingDTO(id_certification=None, id_diploma=1))
    assert training.id_certification is None
    assert training.id_diploma == 1
