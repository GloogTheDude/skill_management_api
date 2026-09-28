import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from core.security import verify_password
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.role_repository import RoleRepository
from dto.employee_dto import CreateEmployeeDTO
from models import AccessLevel, Base, Employee, Role
from services.employee_service import EmployeeService


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(AccessLevel(id_access_level=1, label="Employee", level=1))
        session.add(Role(id_role=1, denomination_role="Employee", id_access_level=1))
        session.commit()
        yield session


def test_employee_create_persists_valid_data_and_hashes_password(session):
    service = EmployeeService(EmployeeRepository(session), RoleRepository(session))

    created = service.create(
        CreateEmployeeDTO(
            first_name="New",
            last_name="Employee",
            password="secret",
            mail="new.employee@example.com",
            id_role=1,
        )
    )

    persisted = session.scalar(
        select(Employee).where(Employee.id_employee == created.id_employee)
    )
    assert persisted is not None
    assert persisted.first_name == "New"
    assert persisted.last_name == "Employee"
    assert persisted.id_role == 1
    assert persisted.hash_password != "secret"
    assert verify_password("secret", persisted.hash_password)
    assert "password" not in created.model_dump()
    assert "hash_password" not in created.model_dump()


def test_employee_delete_is_a_soft_delete(session):
    employee = Employee(
        first_name="Existing",
        last_name="Employee",
        mail="existing.employee@example.com",
        hash_password="argon2-hash",
        id_role=1,
    )
    session.add(employee)
    session.flush()
    employee_id = employee.id_employee

    service = EmployeeService(EmployeeRepository(session), RoleRepository(session))
    service.delete(employee_id)

    persisted = session.get(Employee, employee_id)
    assert persisted is not None
    assert persisted.is_deleted is True
    assert session.scalar(
        select(Employee.id_employee).where(Employee.id_employee == employee_id)
    ) == employee_id


def test_employee_repository_get_all_excludes_soft_deleted_employees(session):
    session.add_all(
        [
            Employee(
                first_name="Active",
                last_name="Employee",
                mail="active.employee@example.com",
                hash_password="argon2-hash",
                id_role=1,
                is_deleted=False,
            ),
            Employee(
                first_name="Deleted",
                last_name="Employee",
                mail="deleted.employee@example.com",
                hash_password="argon2-hash",
                id_role=1,
                is_deleted=True,
            ),
        ]
    )
    session.flush()

    employees = EmployeeRepository(session).get_all()

    assert {employee.mail for employee in employees} == {"active.employee@example.com"}
