import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models import Base
from models.employee import Employee


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def employee(mail, *, is_deleted=False):
    return Employee(
        first_name="Test",
        last_name="User",
        mail=mail,
        hash_password="argon2-hash",
        id_role=1,
        is_deleted=is_deleted,
    )


def test_active_employee_mail_is_unique_in_database(session):
    session.add_all([employee("same@example.com"), employee("same@example.com")])
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    assert session.query(Employee).count() == 0


def test_soft_deleted_employee_mail_can_be_reused(session):
    session.add(employee("reusable@example.com", is_deleted=True))
    session.commit()

    session.add(employee("reusable@example.com"))
    session.commit()

    assert session.query(Employee).count() == 2
