from sqlalchemy.exc import NoResultFound

from db.repositories.employee_declared_skill_repository import EmployeeDeclaredSkillRepository
from dto.employee_declared_skill_dto import CreateEmployeeDeclaredSkillDTO, ResponseEmployeeDeclaredSkillDTO, UpdateEmployeeDeclaredSkillDTO
from models.employee_declared_skill import EmployeeDeclaredSkill
from models.employee import Employee
from models.skill import Skill


class EmployeeDeclaredSkillService:
    def __init__(self, repository: EmployeeDeclaredSkillRepository):
        self.repository = repository

    @staticmethod
    def _response(entity):
        return ResponseEmployeeDeclaredSkillDTO(
            id_employee_declared_skill=entity.id_employee_declared_skill,
            id_employee=entity.id_employee,
            id_skill=entity.id_skill,
            skill_name=entity.skill.name_skill if entity.skill else None,
            skill_domaine=entity.skill.domaine.nom_domaine if entity.skill and entity.skill.domaine else None,
            level=entity.level,
            acquired_at=entity.acquired_at,
        )

    def get_for_employee(self, employee_id):
        return [self._response(item) for item in self.repository.get_for_employee(employee_id)]

    def create(self, dto: CreateEmployeeDeclaredSkillDTO):
        session = self.repository._session
        employee = session.get(Employee, dto.id_employee)
        skill = session.get(Skill, dto.id_skill)
        if employee is None or employee.is_deleted or skill is None or skill.is_deleted:
            raise NoResultFound()
        existing = self.repository.get_by_employee_skill(dto.id_employee, dto.id_skill)
        if existing is not None:
            if not existing.is_deleted:
                raise ValueError("A declared acquisition already exists for this Employee and Skill.")
            existing.is_deleted = False
            existing.level = dto.level
            existing.acquired_at = dto.acquired_at
            self.repository._session.flush()
            return self._response(existing)
        return self._response(self.repository.create(dto.id_employee, dto.id_skill, dto.level, dto.acquired_at))

    def update(self, entity_id, dto: UpdateEmployeeDeclaredSkillDTO):
        entity = self.repository.get_one(entity_id)
        if entity.is_deleted:
            raise NoResultFound()
        return self._response(self.repository.update(entity_id, **dto.model_dump(exclude_unset=True)))

    def archive(self, entity_id):
        return self._response(self.repository.soft_delete(entity_id))
