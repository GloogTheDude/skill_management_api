from datetime import date

from pydantic import BaseModel


class EmployeeCertificationExpirationDTO(BaseModel):
    id_employee_certification: int
    employee_id: int
    employee_first_name: str | None
    employee_last_name: str | None
    certification_id: int
    certification_name: str | None
    expiration_date: date
    status: str
