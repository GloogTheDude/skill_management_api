from datetime import date

from pydantic import BaseModel, Field

from models.employee_diploma import EmployeeDiploma


class ResponseEmployeeDiplomaDTO(BaseModel):
    id_employee: int
    id_diploma: int
    end_: date | None
    school: str | None
    start_: date | None
    distinction: str | None
    doc: str | None

    @classmethod
    def from_entity(
        cls,
        employee_diploma: EmployeeDiploma,
    ):
        return cls(
            id_employee=employee_diploma.id_employee,
            id_diploma=employee_diploma.id_diploma,
            end_=employee_diploma.end_,
            school=employee_diploma.school,
            start_=employee_diploma.start_,
            distinction=employee_diploma.distinction,
            doc=employee_diploma.doc,
        )


class CreateEmployeeDiplomaDTO(BaseModel):
    id_employee: int = Field(gt=0)
    id_diploma: int = Field(gt=0)
    end_: date | None = None
    school: str | None = Field(default=None, max_length=50)
    start_: date | None = None
    distinction: str | None = Field(default=None, max_length=50)
    doc: str | None = Field(default=None, max_length=50)


class UpdateEmployeeDiplomaDTO(BaseModel):
    end_: date | None = None
    school: str | None = Field(default=None, max_length=50)
    start_: date | None = None
    distinction: str | None = Field(default=None, max_length=50)
    doc: str | None = Field(default=None, max_length=50)
