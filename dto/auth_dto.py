from pydantic import BaseModel, Field

from models.employee import Employee


class LoginDTO(BaseModel):
    mail: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthEmployeeDTO(BaseModel):
    id_employee: int
    first_name: str | None
    last_name: str | None
    mail: str | None
    role_name: str | None
    access_level_label: str | None
    access_level: int | None

    @classmethod
    def from_entity(cls, employee: Employee) -> "AuthEmployeeDTO":
        role = employee.role
        access_level = role.access_level if role is not None else None
        return cls(
            id_employee=employee.id_employee,
            first_name=employee.first_name,
            last_name=employee.last_name,
            mail=employee.mail,
            role_name=role.denomination_role if role is not None else None,
            access_level_label=(
                access_level.label if access_level is not None else None
            ),
            access_level=access_level.level if access_level is not None else None,
        )
