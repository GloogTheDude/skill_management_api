from pydantic import BaseModel, Field, model_validator

from models.employee import Employee


class ResponseEmployeeDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    mail: str | None

    id_role: int
    denomination_role: str | None
    id_access_level: int | None = None
    access_level_label: str | None = None
    access_level: int | None = None
    permission_profile: str | None = None

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
            id_access_level=employee.role.id_access_level,
            access_level_label=employee.role.access_level.label if employee.role.access_level else None,
            access_level=employee.role.access_level.level if employee.role.access_level else None,
            permission_profile=(employee.role.access_level.permission_profile if employee.role.access_level else None),
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

    password: str = Field(min_length=1)

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

    password: str | None = Field(default=None, min_length=1)

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null_password(cls, values):
        if isinstance(values, dict) and "password" in values and values["password"] is None:
            raise ValueError("password cannot be null when provided")
        return values

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
