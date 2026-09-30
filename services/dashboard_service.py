from datetime import date, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from core.constants import PARTICIPATIONSTATUS, PermissionProfile
from db.repositories.acquisition_skill_repository import AcquisitionSkillRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.skill_validation_repository import SkillValidationRepository
from models.certification import Certification
from models.employee import Employee
from models.employee_certification import EmployeeCertification
from models.participation import Participation
from models.role import Role
from models.access_level import AccessLevel
from models.skill_validation import SkillValidation
from models.training_request import TrainingRequest
from dto.auth_dto import AuthEmployeeDTO
from dto.dashboard_dto import DashboardDTO
from services.employee_skill_profile_service import EmployeeSkillProfileService


class DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def get_dashboard(self, current: AuthEmployeeDTO) -> DashboardDTO:
        employee_scope = self._scope(current)
        scope_filter = Employee.id_employee.in_(employee_scope)

        pending_requests = self.session.scalar(
            select(func.count(TrainingRequest.id_training_request)).join(
                Employee, Employee.id_employee == TrainingRequest.id_employee
            ).where(
                TrainingRequest.status == "PENDING",
                TrainingRequest.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
                scope_filter,
            )
        ) or 0
        active_participations = self.session.scalar(
            select(func.count()).select_from(Participation).join(
                Employee, Employee.id_employee == Participation.id_employee
            ).where(
                Participation.status.in_((
                    PARTICIPATIONSTATUS.REGISTERED.value,
                    PARTICIPATIONSTATUS.IN_PROGRESS.value,
                )),
                Participation.is_deleted.is_(False),
                Employee.is_deleted.is_(False),
                scope_filter,
            )
        ) or 0
        today = date.today()
        expiring_certifications = self.session.scalar(
            select(func.count(EmployeeCertification.id_employee_certification)).join(
                Employee, Employee.id_employee == EmployeeCertification.id_employee
            ).join(
                Certification,
                Certification.id_certification == EmployeeCertification.id_certification,
            ).where(
                EmployeeCertification.is_deleted.is_(False),
                EmployeeCertification.expiration >= today,
                EmployeeCertification.expiration <= today + timedelta(days=30),
                Employee.is_deleted.is_(False),
                Certification.is_deleted.is_(False),
                scope_filter,
            )
        ) or 0
        pending_evaluations = len(
            SkillValidationRepository(self.session).get_pending_evaluations_for_scope(
                current.id_employee, current.permission_profile
            )
        )

        result = DashboardDTO(
            pending_training_requests=pending_requests,
            pending_skill_evaluations=pending_evaluations,
            active_participations=active_participations,
            expiring_certifications=expiring_certifications,
        )
        if current.permission_profile == PermissionProfile.HR:
            result.active_employees = self.session.scalar(
                select(func.count(Employee.id_employee)).where(Employee.is_deleted.is_(False))
            ) or 0
        elif current.permission_profile == PermissionProfile.MANAGER:
            result.active_employees = len(employee_scope)
        else:
            profile = EmployeeSkillProfileService(
                EmployeeRepository(self.session),
                AcquisitionSkillRepository(self.session),
            ).get_profile(current.id_employee)
            result.acquired_skills = sum(item.acquired_level is not None for item in profile)
            result.evaluated_skills = sum(item.evaluated_level is not None for item in profile)
        return result

    def _scope(self, current: AuthEmployeeDTO) -> list[int]:
        if current.permission_profile == PermissionProfile.HR:
            return list(self.session.scalars(
                select(Employee.id_employee).where(Employee.is_deleted.is_(False))
            ).all())
        if current.permission_profile == PermissionProfile.MANAGER:
            return list(self.session.scalars(
                select(Employee.id_employee).where(
                    Employee.is_deleted.is_(False),
                    or_(Employee.id_employee == current.id_employee,
                        Employee.id_manager == current.id_employee),
                )
            ).all())
        return [current.id_employee]
