from core.database import SessionLocal
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.role_repository import RoleRepository
from menus.employee_crud_menu import EmployeeCrudMenu
from services.employee_service import EmployeeService


class EmployeeCrudController:
    def main_menu(self) -> None:
        user_choice = -1

        while user_choice != 0:
            user_choice = EmployeeCrudMenu.main_menu()

            match user_choice:
                case 1:
                    self.list_employees()
                case 2:
                    self.create_employee()
                case 3:
                    self.update_employee()
                case 4:
                    self.delete_employee()
                case 0:
                    return

    def list_employees(self) -> None:
        with SessionLocal() as session:
            employee_repo = EmployeeRepository(session)
            service = EmployeeService(employee_repo)

            employees = service.get_all_for_crud()

        EmployeeCrudMenu.display_employees(employees)

    def create_employee(self) -> None:
        first_name = EmployeeCrudMenu.ask_first_name()
        last_name = EmployeeCrudMenu.ask_last_name()
        mail = EmployeeCrudMenu.ask_mail()
        hash_password = EmployeeCrudMenu.ask_password()
        id_role = EmployeeCrudMenu.ask_id_role()
        id_manager = EmployeeCrudMenu.ask_id_manager()

        if not first_name or not last_name or not mail or not hash_password:
            EmployeeCrudMenu.display_error(
                "First name, last name, mail and password cannot be empty."
            )
            return

        with SessionLocal() as session:
            try:
                employee_repo = EmployeeRepository(session)
                role_repo = RoleRepository(session)
                service = EmployeeService(employee_repo, role_repo)

                created = service.create(
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    hash_password=hash_password,
                    id_role=id_role,
                    id_manager=id_manager,
                )

                if created is None:
                    session.rollback()
                    EmployeeCrudMenu.display_error(
                        "Invalid employee data. Check role, manager or duplicate mail."
                    )
                    return

                session.commit()
                EmployeeCrudMenu.display_success("Employee created.")
            except Exception:
                session.rollback()
                raise

    def update_employee(self) -> None:
        id_employee = EmployeeCrudMenu.ask_id_employee()
        first_name = EmployeeCrudMenu.ask_first_name()
        last_name = EmployeeCrudMenu.ask_last_name()
        mail = EmployeeCrudMenu.ask_mail()
        hash_password = EmployeeCrudMenu.ask_optional_password()
        id_role = EmployeeCrudMenu.ask_id_role()
        id_manager = EmployeeCrudMenu.ask_id_manager()

        if not first_name or not last_name or not mail:
            EmployeeCrudMenu.display_error(
                "First name, last name and mail cannot be empty."
            )
            return

        with SessionLocal() as session:
            try:
                employee_repo = EmployeeRepository(session)
                role_repo = RoleRepository(session)
                service = EmployeeService(employee_repo, role_repo)

                updated = service.update(
                    id_employee=id_employee,
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    hash_password=hash_password,
                    id_role=id_role,
                    id_manager=id_manager,
                )

                if updated is None:
                    session.rollback()
                    EmployeeCrudMenu.display_error(
                        "Employee not found or invalid employee data."
                    )
                    return

                session.commit()
                EmployeeCrudMenu.display_success("Employee updated.")
            except Exception:
                session.rollback()
                raise

    def delete_employee(self) -> None:
        id_employee = EmployeeCrudMenu.ask_id_employee()

        with SessionLocal() as session:
            try:
                employee_repo = EmployeeRepository(session)
                service = EmployeeService(employee_repo)

                deleted = service.delete(id_employee)

                if not deleted:
                    session.rollback()
                    EmployeeCrudMenu.display_error("Employee not found.")
                    return

                session.commit()
                EmployeeCrudMenu.display_success("Employee deleted.")
            except Exception:
                session.rollback()
                raise