from pydantic import BaseModel


class DashboardDTO(BaseModel):
    pending_training_requests: int
    pending_skill_evaluations: int
    active_participations: int
    expiring_certifications: int
    active_employees: int | None = None
    acquired_skills: int | None = None
    evaluated_skills: int | None = None
