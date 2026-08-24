from services.login_service import LoginService
from dto.employee_dto import EmployeeDTO

class LoginController:

    def __init__(self, login_service: LoginService):
        self.login_service = login_service

    def login(self, mail: str, password: str) -> tuple[bool, EmployeeDTO | None, str | None]:
        employee_dto= self.login_service.login(mail, password)

        if employee_dto is None:
            print("Invalid credentials")
            return False, None, "Invalid credentials"
        

        print("Credentials OK")
        return True, employee_dto, "Credentials OK"