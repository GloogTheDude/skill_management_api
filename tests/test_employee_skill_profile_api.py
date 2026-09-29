from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from core.constants import PARTICIPATIONSTATUS
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from dto.skill_dto import SkillProfileDTO
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
from services.employee_skill_profile_service import EmployeeSkillProfileService


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
            Domaine(id_domaine=2, nom_domaine="Archived", is_deleted=True),
            Employee(
                id_employee=1,
                first_name="Ada",
                last_name="Lovelace",
                hash_password="hash",
                mail="ada@example.com",
                id_role=1,
                is_deleted=False,
            ),
            Skill(id_skill=1, name_skill="Python", id_domaine=1, is_deleted=False),
            Skill(id_skill=2, name_skill="SQL", id_domaine=1, is_deleted=False),
            Skill(id_skill=3, name_skill="Archived skill", id_domaine=2, is_deleted=False),
            ValidationType(
                id_validation=1,
                source="manual",
                denomination_validation="Manager validation",
                is_deleted=False,
            ),
            Diploma(
                id_diploma=1,
                subject_diploma="Computer Science",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=1,
                subject_certification="Python Professional",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=2,
                subject_certification="Expired Python",
                id_domaine=1,
                is_deleted=False,
            ),
            Training(
                id_training=1,
                title="Python workshop",
                id_domaine=1,
                start_=date.today() - timedelta(days=20),
                end_=date.today() - timedelta(days=10),
                is_deleted=False,
            ),
            Training(
                id_training=2,
                title="Certification workshop",
                id_domaine=1,
                id_certification=1,
                is_deleted=False,
            ),
            Training(
                id_training=3,
                title="Deleted workshop",
                id_domaine=1,
                is_deleted=True,
            ),
            TrainingSkill(
                id_training=1,
                id_skill=1,
                granted_level=2,
                is_deleted=False,
            ),
            TrainingSkill(
                id_training=2,
                id_skill=2,
                granted_level=5,
                is_deleted=False,
            ),
            TrainingSkill(
                id_training=3,
                id_skill=3,
                granted_level=5,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=1,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=2,
                status=PARTICIPATIONSTATUS.COMPLETED.value,
                is_deleted=False,
            ),
            Participation(
                id_employee=1,
                id_training=3,
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
                start_=date.today() - timedelta(days=20),
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
            DiplomaSkill(
                id_diploma=1,
                id_skill=1,
                min_level=None,
                is_deleted=False,
            ),
            CertificationSkill(
                id_certification=1,
                id_skill=1,
                granted_level=3,
                is_deleted=False,
            ),
            CertificationSkill(
                id_certification=2,
                id_skill=1,
                granted_level=5,
                is_deleted=False,
            ),
            SkillValidation(
                id_skill_validation=1,
                date_=date.today(),
                level_skill=3,
                id_validation=1,
                id_employee=1,
                id_validator=1,
                id_skill=1,
                is_deleted=False,
            ),
        ]
    )
    current_session.commit()
    yield current_session
    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def profile_service(session):
    return EmployeeSkillProfileService(
        EmployeeRepository(session),
        AcquisitionSkillRepository(session),
    )


def test_profile_consolidates_sources_and_uses_active_highest_level(session):
    result = profile_service(session).get_profile(1)

    assert all(isinstance(profile, SkillProfileDTO) for profile in result)
    python = next(profile for profile in result if profile.skill_id == 1)

    assert python.displayed_level == 3
    assert python.primary_source.source_type == "CERTIFICATION"
    assert python.acquired_level == 3
    assert python.evaluated_level == 3
    assert python.primary_acquired_source.source_type == "CERTIFICATION"
    assert python.current_validation.id_skill_validation == 1
    assert [source.source_type for source in python.sources] == [
        "TRAINING",
        "CERTIFICATION",
        "CERTIFICATION",
        "DIPLOMA",
        "VALIDATION",
    ]
    expired = next(source for source in python.sources if source.source_id == 2)
    assert expired.is_active is False


def test_acquired_and_evaluated_levels_are_independent(session):
    validation = session.get(SkillValidation, 1)
    validation.level_skill = 2
    session.commit()

    python = next(
        profile for profile in profile_service(session).get_profile(1)
        if profile.skill_id == 1
    )

    assert python.acquired_level == 3
    assert python.evaluated_level == 2
    assert python.current_validation.level == 2


def test_soft_deleted_current_validation_is_not_evaluated(session):
    validation = session.get(SkillValidation, 1)
    validation.is_deleted = True
    session.commit()

    python = next(
        profile for profile in profile_service(session).get_profile(1)
        if profile.skill_id == 1
    )

    assert python.acquired_level == 3
    assert python.evaluated_level is None
    assert python.current_validation is None


def test_training_only_contributes_when_completed_and_without_qualification(session):
    result = profile_service(session).get_profile(1)

    assert {profile.skill_id for profile in result} == {1, 3}


def test_soft_deleted_training_skill_and_skill_are_excluded(session):
    session.get(TrainingSkill, (1, 1)).is_deleted = True
    session.get(Skill, 1).is_deleted = True
    session.commit()

    result = profile_service(session).get_profile(1)
    assert {profile.skill_id for profile in result} == {3}


def test_null_levels_and_soft_deleted_domain_are_preserved(session):
    session.add(
        DiplomaSkill(
            id_diploma=1,
            id_skill=3,
            min_level=None,
            is_deleted=False,
        )
    )
    session.commit()

    result = profile_service(session).get_profile(1)
    archived = next(profile for profile in result if profile.skill_id == 3)

    assert archived.skill_domaine == "Archived"
    diploma_source = next(source for source in archived.sources if source.source_type == "DIPLOMA")
    assert diploma_source.level is None


def test_deleted_employee_is_not_available(session):
    session.get(Employee, 1).is_deleted = True
    session.commit()

    with pytest.raises(NoResultFound):
        profile_service(session).get_profile(1)
