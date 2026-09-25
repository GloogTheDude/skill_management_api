from db.repositories.base_repository import BaseRepository
from models.employee import Employee


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee