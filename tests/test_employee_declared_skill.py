from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Employee, Skill
from models.employee_declared_skill import EmployeeDeclaredSkill
from db.repositories.employee_declared_skill_repository import EmployeeDeclaredSkillRepository
from dto.employee_declared_skill_dto import CreateEmployeeDeclaredSkillDTO
from services.employee_declared_skill_service import EmployeeDeclaredSkillService
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from services.employee_skill_profile_service import EmployeeSkillProfileService


def test_declared_skill_can_be_created_and_read():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        Employee(id_employee=1, id_role=1, is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
    ])
    session.commit()

    repository = EmployeeDeclaredSkillRepository(session)
    created = repository.create(1, 1, 3, date(2026, 1, 15))

    assert created.level == 3
    assert repository.get_for_employee(1)[0].id_skill == 1

    session.close()
    engine.dispose()


def test_declared_skill_is_aggregated_as_acquired_only():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        Employee(id_employee=1, id_role=1, is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
    ])
    session.commit()
    EmployeeDeclaredSkillService(EmployeeDeclaredSkillRepository(session)).create(
        CreateEmployeeDeclaredSkillDTO(id_employee=1, id_skill=1, level=3)
    )

    profile = EmployeeSkillProfileService(
        type("Employees", (), {"get_one": lambda self, employee_id: session.get(Employee, employee_id)})(),
        AcquisitionSkillRepository(session),
    ).get_profile(1)

    assert profile[0].acquired_level == 3
    assert [source.source_type for source in profile[0].acquired_sources] == ["DECLARED"]
    assert profile[0].evaluated_level is None
    assert session.query(__import__("models").SkillValidation).count() == 0

    session.close()
    engine.dispose()


def test_declared_skill_level_is_limited_to_one_through_five():
    for level in (0, 6):
        try:
            CreateEmployeeDeclaredSkillDTO(id_employee=1, id_skill=1, level=level)
        except ValueError:
            continue
        raise AssertionError("invalid declared level was accepted")


def test_archived_declared_skill_is_excluded_and_can_be_restored():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([
        Employee(id_employee=1, id_role=1, is_deleted=False),
        Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
    ])
    session.commit()
    service = EmployeeDeclaredSkillService(EmployeeDeclaredSkillRepository(session))
    created = service.create(CreateEmployeeDeclaredSkillDTO(id_employee=1, id_skill=1, level=3))
    EmployeeDeclaredSkillRepository(session).soft_delete(created.id_employee_declared_skill)
    assert EmployeeDeclaredSkillRepository(session).get_for_employee(1) == []
    restored = service.create(CreateEmployeeDeclaredSkillDTO(id_employee=1, id_skill=1, level=4))
    assert restored.level == 4
    assert len(EmployeeDeclaredSkillRepository(session).get_for_employee(1)) == 1
    session.close()
    engine.dispose()
