from datetime import date, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from core.constants import PARTICIPATIONSTATUS
from db.repositories.employee_skill_search_repository import (
    EmployeeSkillSearchRepository,
)
from dto.employee_skill_search_dto import (
    EmployeeSkillSearchRequestDTO,
)
from dto.auth_dto import AuthEmployeeDTO
from errors.authorization_errors import AuthorizationForbidden
from models import Base
from models.access_level import AccessLevel
from models.certification import Certification
from models.certification_skill import CertificationSkill
from models.diploma import Diploma
from models.diploma_skill import DiplomaSkill
from models.domaine import Domaine
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from models.employee_diploma import EmployeeDiploma
from models.participation import Participation
from models.role import Role
from models.skill import Skill
from models.skill_validation import SkillValidation
from models.training import Training
from models.training_skill import TrainingSkill
from models.validation_type import ValidationType
from services.employee_skill_search_service import EmployeeSkillSearchService


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    current_session = sessionmaker(bind=engine)()
    current_session.add_all(
        [
            AccessLevel(id_access_level=1, label="Employee", level=1),
            Role(id_role=1, denomination_role="Employee", id_access_level=1),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
            Employee(
                id_employee=1,
                first_name="Ada",
                last_name="Lovelace",
                hash_password="hash",
                mail="ada@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Employee(
                id_employee=2,
                first_name="Grace",
                last_name="Hopper",
                hash_password="hash",
                mail="grace@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Employee(
                id_employee=3,
                first_name="Deleted",
                last_name="Employee",
                hash_password="hash",
                mail="deleted@example.com",
                id_role=1,
                is_deleted=True,
            ),
            Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
            Skill(id_skill=2, name_skill="SQL", id_domaine=1, is_deleted=False),
            Skill(id_skill=3, name_skill="No level", id_domaine=1, is_deleted=False),
            Skill(id_skill=4, name_skill="Expired only", id_domaine=1, is_deleted=False),
            Skill(id_skill=5, name_skill="Not completed", id_domaine=1, is_deleted=False),
            Skill(id_skill=6, name_skill="Qualification training", id_domaine=1, is_deleted=False),
            Skill(id_skill=7, name_skill="Deleted source", id_domaine=1, is_deleted=False),
            Diploma(
                id_diploma=1,
                subject_diploma="Computer Science",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=1,
                subject_certification="Python Active",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=2,
                subject_certification="Python Expired",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=3,
                subject_certification="Expired Only",
                id_domaine=1,
                is_deleted=False,
            ),
            Training(
                id_training=1,
                title="Completed Python",
                id_domaine=1,
                is_deleted=False,
            ),
            Training(
                id_training=2,
                title="In progress SQL",
                id_domaine=1,
                is_deleted=False,
            ),
            Training(
                id_training=3,
                title="Qualification training",
                id_domaine=1,
                id_certification=1,
                is_deleted=False,
            ),
            Training(
                id_training=4,
                title="Deleted source training",
                id_domaine=1,
                is_deleted=True,
            ),
            TrainingSkill(id_training=1, id_skill=1, granted_level=2, is_deleted=False),
            TrainingSkill(id_training=2, id_skill=2, granted_level=5, is_deleted=False),
            TrainingSkill(id_training=3, id_skill=6, granted_level=5, is_deleted=False),
            TrainingSkill(id_training=4, id_skill=7, granted_level=5, is_deleted=False),
            Participation(
                id_employee=1,
                id_training=1,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=2,
                status=PARTICIPATIONSTATUS.IN_PROGRESS.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=3,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=4,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=2,
                id_training=1,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            EmployeeDiploma(
                id_employee=1,
                id_diploma=1,
                end_=date.today(),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=1,
                id_employee=1,
                id_certification=1,
                expiration=date.today(),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=2,
                id_employee=1,
                id_certification=2,
                expiration=date.today() - timedelta(days=1),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=3,
                id_employee=1,
                id_certification=3,
                expiration=date.today() - timedelta(days=1),
                is_deleted=False,
            ),
            DiplomaSkill(id_diploma=1, id_skill=2, min_level=4, is_deleted=False),
            DiplomaSkill(id_diploma=1, id_skill=3, min_level=None, is_deleted=False),
            CertificationSkill(id_certification=1, id_skill=1, granted_level=3, is_deleted=False),
            CertificationSkill(id_certification=2, id_skill=1, granted_level=5, is_deleted=False),
            CertificationSkill(id_certification=3, id_skill=4, granted_level=5, is_deleted=False),
            ValidationType(
                id_validation=1,
                source="manual",
                denomination_validation="Manager validation",
                is_deleted=False,
            ),
            SkillValidation(
                id_skill_validation=1,
                date_=date.today(),
                level_skill=4,
                id_validation=1,
                id_employee=1,
                id_validator=1,
                id_skill=1,
                is_deleted=False,
            ),
            SkillValidation(
                id_skill_validation=2,
                date_=date.today(),
                level_skill=None,
                id_validation=1,
                id_employee=1,
                id_validator=1,
                id_skill=3,
                is_deleted=False,
            ),
        ]
    )
    current_session.commit()
    yield current_session
    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def search_service(session):
    return EmployeeSkillSearchService(EmployeeSkillSearchRepository(session))


def requirement(id_skill, operator="gte", level=1):
    return {"id_skill": id_skill, "operator": operator, "level": level}


def search(session, *requirements):
    return search_service(session).search(
        EmployeeSkillSearchRequestDTO(requirements=list(requirements))
    )


def actor(id_employee, access_level):
    return AuthEmployeeDTO(
        id_employee=id_employee,
        first_name="Actor",
        last_name="Test",
        mail="actor@example.com",
        role_name=None,
        access_level_label=None,
        access_level=access_level,
    )


def test_simple_requirement_returns_matching_employee(session):
    result = search(session, requirement(1, "gte", 3))

    assert [employee.id_employee for employee in result] == [1]


def test_multiple_requirements_use_and_logic(session):
    result = search(
        session,
        requirement(1, "gte", 3),
        requirement(2, "gte", 4),
    )

    assert [employee.id_employee for employee in result] == [1]


def test_acquired_or_evaluated_satisfies_one_requirement(session):
    assert [employee.id_employee for employee in search(session, requirement(1, "gte", 4))] == [1]
    assert [employee.id_employee for employee in search(session, requirement(1, "lte", 3))] == [1, 2]


def test_evaluated_filter_ignores_superseded_and_acquired_filter_ignores_validation(session):
    validation = session.get(SkillValidation, 1)
    validation.level_skill = 2
    validation.superseded_at = date.today()
    session.add(SkillValidation(
        id_skill_validation=3,
        date_=date.today(),
        level_skill=1,
        id_validation=1,
        id_employee=1,
        id_validator=1,
        id_skill=1,
        is_deleted=False,
    ))
    session.commit()

    assert search(session, requirement(1, "gte", 4)) == []
    assert [employee.id_employee for employee in search(session, requirement(1, "gte", 3))] == [1]


def test_requirement_level_one_requires_an_active_dimension(session):
    assert search(session, requirement(3, "gte", 1)) == []


def test_none_level_does_not_match_numeric_requirement(session):
    assert search(session, requirement(3, "gte", 1)) == []


def test_active_sources_use_highest_relevant_level(session):
    result = search(session, requirement(1, "gte", 3))

    skill = next(skill for skill in result[0].skills if skill.skill_id == 1)
    assert skill.displayed_level == 4


def test_expired_only_source_does_not_match(session):
    assert search(session, requirement(4, "gte", 1)) == []


def test_expired_source_does_not_raise_active_matching_level(session):
    assert search(session, requirement(1, "gte", 5)) == []
    assert [employee.id_employee for employee in search(session, requirement(1, "gte", 3))] == [1]


def test_non_completed_training_does_not_match(session):
    session.add(TrainingSkill(id_training=2, id_skill=5, granted_level=5, is_deleted=False))
    session.commit()

    assert search(session, requirement(5, "gte", 1)) == []


def test_qualification_training_does_not_add_training_source(session):
    result = search(session, requirement(6, "gte", 1))
    assert result == []


def test_soft_deleted_sources_and_deleted_employees_are_excluded(session):
    session.get(TrainingSkill, (1, 1)).is_deleted = True
    session.get(Employee, 2).is_deleted = True
    session.commit()

    result = search(session, requirement(1, "gte", 1))

    assert [employee.id_employee for employee in result] == [1]
    assert all(employee.id_employee != 2 for employee in result)


def test_result_contains_all_consolidated_skills_without_cartesian_product(session):
    result = search(session, requirement(1, "gte", 3))

    assert len(result) == 1
    assert result[0].id_employee == 1
    assert {skill.skill_id for skill in result[0].skills} == {1, 2, 3, 4}


def test_empty_requirements_are_rejected():
    with pytest.raises(ValidationError):
        EmployeeSkillSearchRequestDTO(requirements=[])


@pytest.mark.parametrize("value", [0, 6])
def test_search_level_bounds_are_rejected(value):
    with pytest.raises(ValidationError):
        EmployeeSkillSearchRequestDTO(requirements=[requirement(1, "gte", value)])


@pytest.mark.parametrize("operator", ["gte", "lte"])
def test_search_operators_are_limited(operator):
    assert EmployeeSkillSearchRequestDTO(
        requirements=[requirement(1, operator, 3)]
    ).requirements[0].operator == operator

    with pytest.raises(ValidationError):
        EmployeeSkillSearchRequestDTO(
            requirements=[requirement(1, "eq", 3)]
        )


def test_employee_cannot_search_and_manager_scope_is_sql_filtered(session):
    employee = session.get(Employee, 2)
    employee.id_manager = 1
    session.commit()
    service = search_service(session)
    dto = EmployeeSkillSearchRequestDTO(requirements=[requirement(1, "gte", 1)])

    with pytest.raises(AuthorizationForbidden):
        service.search(dto, actor(2, 1))

    result = service.search(dto, actor(1, 2))
    assert {item.id_employee for item in result} == {2}


def test_manager_search_excludes_non_direct_reports(session):
    employee = session.get(Employee, 2)
    employee.id_manager = 2
    session.commit()
    dto = EmployeeSkillSearchRequestDTO(requirements=[requirement(1, "gte", 1)])

    result = search_service(session).search(dto, actor(1, 2))
    assert result == []
