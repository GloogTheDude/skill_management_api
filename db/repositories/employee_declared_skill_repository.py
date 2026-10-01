from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.repositories.base_repository import BaseRepository
from models.employee_declared_skill import EmployeeDeclaredSkill


class EmployeeDeclaredSkillRepository(BaseRepository[EmployeeDeclaredSkill]):
    model = EmployeeDeclaredSkill

    def create(self, id_employee, id_skill, level, acquired_at=None):
        return self.add(EmployeeDeclaredSkill(
            id_employee=id_employee, id_skill=id_skill, level=level, acquired_at=acquired_at,
        ))

    def get_by_employee_skill(self, id_employee, id_skill):
        return self._session.scalar(select(EmployeeDeclaredSkill).where(
            EmployeeDeclaredSkill.id_employee == id_employee,
            EmployeeDeclaredSkill.id_skill == id_skill,
        ))

    def get_for_employee(self, id_employee):
        statement = select(EmployeeDeclaredSkill).options(
            joinedload(EmployeeDeclaredSkill.skill),
        ).where(
            EmployeeDeclaredSkill.id_employee == id_employee,
            EmployeeDeclaredSkill.is_deleted.is_(False),
        )
        return list(self._session.scalars(statement).all())
