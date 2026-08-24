from core.database import SessionLocal
from db.repositories.employee_repository import EmployeeRepository
from services.login_service import LoginService
from controllers.login_controller import LoginController
from controllers.employee_controller import EmployeeController
from controllers.manager_controller import ManagerController
from controllers.hr_controller import HRController


def main():
    

    mail = input("Mail: ")
    password = input("Password: ")

    with SessionLocal() as session:
        employee_repo = EmployeeRepository(session)
        login_serv = LoginService(employee_repo)
        login_control = LoginController(login_serv)
        succes,employee_dto,extra = login_control.login(mail, password)
        print(extra)
    
    if succes and employee_dto:
        print(f"access_label = {employee_dto.access_label}")
        role = employee_dto.access_label
        if role == "Employee":
            employee_controller = EmployeeController(employee_dto)
            employee_controller.get_main_employee_menu()
        elif role == "Manager":
            manager_controller = ManagerController(employee_dto)
            manager_controller.get_main_manager_menu()
        elif role == "HR":
            hr_controller = HRController(employee_dto)
            hr_controller.get_main_hr_menu()
    else:
        print("not a valid login/password")


if __name__ == "__main__":
    main()