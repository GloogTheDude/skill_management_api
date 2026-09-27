from core.security import hash_password, verify_password
from dto.employee_dto import CreateEmployeeDTO, ResponseEmployeeDTO, UpdateEmployeeDTO
from models.employee import Employee
from models.role import Role
from services.employee_service import EmployeeService


class FakeEmployeeRepository:
    def __init__(self, employee: Employee | None = None):
        self.employee = employee

    def add(self, employee: Employee) -> Employee:
        self.employee = employee
        employee.id_employee = 1
        employee.role = Role(id_role=employee.id_role, denomination_role="Employee")
        return employee

    def update(self, _id_employee: int, **kwargs) -> Employee:
        for field, value in kwargs.items():
            setattr(self.employee, field, value)
        return self.employee


def employee_with_password(password: str) -> Employee:
    employee = Employee(
        id_employee=1,
        first_name="Test",
        last_name="Employee",
        hash_password=hash_password(password),
        mail="test@example.com",
        id_role=1,
    )
    employee.role = Role(id_role=1, denomination_role="Employee")
    return employee


def test_hash_and_verify_password():
    hashed = hash_password("secret")

    assert hashed.startswith("$argon2id$")
    assert hashed != "secret"
    assert verify_password("secret", hashed) is True
    assert verify_password("wrong", hashed) is False
    assert verify_password("secret", "not-an-argon2-hash") is False


def test_hash_password_uses_a_new_salt_each_time():
    first = hash_password("secret")
    second = hash_password("secret")

    assert first != second
    assert verify_password("secret", first) is True
    assert verify_password("secret", second) is True


def test_employee_creation_stores_an_argon2_hash():
    repository = FakeEmployeeRepository()
    service = EmployeeService(repository)

    service.create(
        CreateEmployeeDTO(
            first_name="Test",
            last_name="Employee",
            password="secret",
            mail="test@example.com",
            id_role=1,
        )
    )

    assert repository.employee.hash_password != "secret"
    assert verify_password("secret", repository.employee.hash_password) is True


def test_employee_password_update_rehashes_the_new_password():
    employee = employee_with_password("old-secret")
    old_hash = employee.hash_password
    repository = FakeEmployeeRepository(employee)
    service = EmployeeService(repository)

    service.update(1, UpdateEmployeeDTO(password="new-secret"))

    assert employee.hash_password != old_hash
    assert verify_password("new-secret", employee.hash_password) is True
    assert verify_password("old-secret", employee.hash_password) is False


def test_employee_update_without_password_preserves_existing_hash():
    employee = employee_with_password("old-secret")
    old_hash = employee.hash_password
    repository = FakeEmployeeRepository(employee)
    service = EmployeeService(repository)

    service.update(1, UpdateEmployeeDTO(first_name="Updated"))

    assert employee.hash_password == old_hash


def test_employee_response_does_not_expose_password_fields():
    response = ResponseEmployeeDTO.from_entity(employee_with_password("secret"))

    assert "password" not in response.model_dump()
    assert "hash_password" not in response.model_dump()


def test_employee_password_dto_rejects_empty_passwords():
    try:
        CreateEmployeeDTO(password="", id_role=1)
    except ValueError:
        pass
    else:
        raise AssertionError("empty create password should be rejected")

    try:
        UpdateEmployeeDTO(password="")
    except ValueError:
        pass
    else:
        raise AssertionError("empty update password should be rejected")

    try:
        UpdateEmployeeDTO(password=None)
    except ValueError:
        pass
    else:
        raise AssertionError("explicit null update password should be rejected")
