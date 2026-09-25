from db.repositories.base_repository import BaseRepository
from models.employee_diploma import EmployeeDiploma


class EmployeeDiplomaRepository(BaseRepository[EmployeeDiploma]):
    model = EmployeeDiploma
