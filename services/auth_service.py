from core.auth import RedisSessionStore
from core.security import verify_password
from db.repositories.employee_repository import EmployeeRepository
from dto.auth_dto import AuthEmployeeDTO


class AuthService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        session_store: RedisSessionStore,
    ):
        self.employee_repository = employee_repository
        self.session_store = session_store

    async def login(self, mail: str, password: str) -> tuple[str, AuthEmployeeDTO] | None:
        employee = self.employee_repository.get_active_by_mail(mail)

        if employee is None or not verify_password(
            password,
            employee.hash_password or "",
        ):
            return None

        session_id = await self.session_store.create(employee.id_employee)
        return session_id, AuthEmployeeDTO.from_entity(employee)

    async def get_current_employee(self, session_id: str) -> AuthEmployeeDTO | None:
        id_employee = await self.session_store.get_employee_id(session_id)
        if id_employee is None:
            return None

        employee = self.employee_repository.get_active_by_id(id_employee)
        if employee is None:
            return None

        return AuthEmployeeDTO.from_entity(employee)

    async def logout(self, session_id: str | None) -> None:
        if session_id:
            await self.session_store.delete(session_id)
