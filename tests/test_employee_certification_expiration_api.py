from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from core.constants import CERTIFICATIONSTATUS
from db.repositories.employee_certification_repository import (
    EmployeeCertificationRepository,
)
from models import Base
from models.access_level import AccessLevel
from models.certification import Certification
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from models.domaine import Domaine
from models.role import Role
from services.employee_certification_service import EmployeeCertificationService


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
    today = date.today()
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
                is_deleted=True,
            ),
            Certification(
                id_certification=1,
                subject_certification="Python",
                id_domaine=1,
                is_deleted=False,
            ),
            Certification(
                id_certification=2,
                subject_certification="SQL",
                id_domaine=1,
                is_deleted=True,
            ),
        ]
    )
    current_session.add_all(
        [
            EmployeeCertification(
                id_employee_certification=1,
                id_employee=1,
                id_certification=1,
                expiration=today - relativedelta(months=3),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=2,
                id_employee=1,
                id_certification=1,
                expiration=today - timedelta(days=1),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=3,
                id_employee=1,
                id_certification=1,
                expiration=today,
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=4,
                id_employee=1,
                id_certification=1,
                expiration=today + relativedelta(months=1),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=5,
                id_employee=1,
                id_certification=1,
                expiration=today + relativedelta(months=1) + timedelta(days=1),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=6,
                id_employee=1,
                id_certification=1,
                expiration=today + relativedelta(months=6),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=7,
                id_employee=1,
                id_certification=1,
                expiration=today + relativedelta(months=6) + timedelta(days=1),
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=8,
                id_employee=1,
                id_certification=1,
                expiration=None,
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=9,
                id_employee=1,
                id_certification=1,
                expiration=today,
                is_deleted=True,
            ),
            EmployeeCertification(
                id_employee_certification=10,
                id_employee=2,
                id_certification=1,
                expiration=today,
                is_deleted=False,
            ),
            EmployeeCertification(
                id_employee_certification=11,
                id_employee=1,
                id_certification=2,
                expiration=today,
                is_deleted=False,
            ),
        ]
    )
    current_session.commit()
    yield current_session
    current_session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def get_expiring(session):
    return EmployeeCertificationService(
        EmployeeCertificationRepository(session)
    ).get_expiring()


def test_expiration_window_is_inclusive_and_none_is_excluded(session):
    result = get_expiring(session)

    assert {item.id_employee_certification for item in result} == {1, 2, 3, 4, 5, 6}
    assert all(item.expiration_date is not None for item in result)


@pytest.mark.parametrize(
    ("certification_id", "expected_status"),
    [
        (2, CERTIFICATIONSTATUS.EXPIRED.value),
        (3, CERTIFICATIONSTATUS.URGENT.value),
        (4, CERTIFICATIONSTATUS.URGENT.value),
        (5, CERTIFICATIONSTATUS.EXPIRING_SOON.value),
    ],
)
def test_expiration_status_uses_legacy_boundaries(
    session, certification_id, expected_status
):
    result = {item.id_employee_certification: item for item in get_expiring(session)}

    assert result[certification_id].status == expected_status


def test_soft_deleted_employee_certification_certification_and_employee_are_excluded(
    session,
):
    result = get_expiring(session)

    assert {item.id_employee_certification for item in result}.isdisjoint({9, 10, 11})


def test_multiple_certifications_are_returned_without_duplicates(session):
    result = get_expiring(session)

    assert len(result) == len({item.id_employee_certification for item in result})
    assert {item.employee_id for item in result} == {1}
    assert {item.certification_id for item in result} == {1}
