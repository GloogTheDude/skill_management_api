from db.repositories.employee_repository import EmployeeRepository
from models.employee import Employee
from dto.employee_dto import EmployeeDTO

class LoginService():
    
    def __init__(self, employee_repo:EmployeeRepository):
        self.employee_repo = employee_repo
    
    def login(self, mail: str, password: str) -> EmployeeDTO | None:
        row = self.employee_repo.get_by_mail_with_access(mail)

        if row is None:
            return None

        employee, role_name, access_label, access_level = row

        # MVP temporaire : comparaison directe.
        # Plus tard : hash sécurisé.
        if employee.hash_password != password:
            return None

        if employee.is_deleted:
            return None

        return EmployeeDTO(
            id_employee=employee.id_employee,
            first_name=employee.first_name,
            last_name=employee.last_name,
            mail=employee.mail,

            id_role=employee.id_role,
            role_name=role_name,

            access_label=access_label,
            access_level=access_level,
        )


