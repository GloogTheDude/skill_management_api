from pydantic import BaseModel, Field

from models.employee import Employee


class ResponseEmployeeDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    mail: str | None

    id_role: int
    denomination_role: str | None

    id_manager: int | None
    manager_name: str | None

    @classmethod
    def from_entity(
        cls,
        employee: Employee,
    ):
        return cls(
            id_employee=employee.id_employee,
            first_name=employee.first_name,
            last_name=employee.last_name,
            mail=employee.mail,
            id_role=employee.id_role,
            denomination_role=employee.role.denomination_role,
            id_manager=employee.id_manager,
            manager_name=(
                f"{employee.manager.first_name} "
                f"{employee.manager.last_name}"
                if employee.manager is not None
                else None
            ),
        )


class CreateEmployeeDTO(BaseModel):
    first_name: str | None = Field(
        default=None,
        max_length=50,
    )
    last_name: str | None = Field(
        default=None,
        max_length=50,
    )

    # POC: currently stored as plain text in Employee.hash_password.
    # Keep the API field named "password" so hashing can later be added
    # in EmployeeService without changing the API contract.
    password: str | None = None

    mail: str | None = Field(
        default=None,
        max_length=50,
    )

    id_role: int = Field(gt=0)
    id_manager: int | None = Field(
        default=None,
        gt=0,
    )


class UpdateEmployeeDTO(BaseModel):
    first_name: str | None = Field(
        default=None,
        max_length=50,
    )
    last_name: str | None = Field(
        default=None,
        max_length=50,
    )

    # POC: currently stored as plain text in Employee.hash_password.
    # Hashing should later remain an implementation detail of EmployeeService.
    password: str | None = None

    mail: str | None = Field(
        default=None,
        max_length=50,
    )

    id_role: int | None = Field(
        default=None,
        gt=0,
    )
    id_manager: int | None = Field(
        default=None,
        gt=0,
    )