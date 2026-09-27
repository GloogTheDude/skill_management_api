from sqlalchemy import select
from sqlalchemy.orm import Session

from core.constants import TRAININGREQUESTSTATUS

from models.training_request import TrainingRequest
from models.training import Training
from models.domaine import Domaine
from models.employee import Employee

class TrainingRequestRepository():
    def __init__(self, session: Session):
        self.session = session

    def add(self, training_request: TrainingRequest):
        self.session.add(training_request)
        self.session.flush()
        return training_request

    def get_active_by_id(self, id_request: int):
        request = self.session.get(TrainingRequest, id_request)
        if request is None or request.is_deleted:
            return None
        return request

    def get_all_with_details(self):
        stmt = (
            select(TrainingRequest, Training.title, Domaine.nom_domaine)
            .outerjoin(TrainingRequest.training)
            .outerjoin(Training.domaine)
            .where(TrainingRequest.is_deleted.is_(False))
        )
        return list(self.session.execute(stmt).all())

    def get_by_id_with_details(self, id_request: int):
        stmt = (
            select(TrainingRequest, Training.title, Domaine.nom_domaine)
            .outerjoin(TrainingRequest.training)
            .outerjoin(Training.domaine)
            .where(TrainingRequest.id_training_request == id_request)
        )
        return self.session.execute(stmt).one_or_none()
    
    def get_for_employee(self, id_employee: int):
        stmt = (
            select(
                TrainingRequest,
                Training.title,
                Domaine.nom_domaine,
            )
            .outerjoin(TrainingRequest.training)
            .outerjoin(Training.domaine)
            .where(TrainingRequest.id_employee == id_employee)
        )
        return self.session.execute(stmt).all()

    def get_pending_for_manager(self, id_manager: int):
        stmt = (
            select(
                TrainingRequest,
                Employee,
                Training,
                Domaine.nom_domaine,
            )
            .join(TrainingRequest.employee)
            .outerjoin(TrainingRequest.training)
            .outerjoin(Training.domaine)
            .where(
                TrainingRequest.status == TRAININGREQUESTSTATUS.PENDING.value,
                TrainingRequest.is_deleted.is_(False),
                Employee.id_manager == id_manager,
            )
        )

        return self.session.execute(stmt).all()
    
    def get_pending_for_hr(self):
        stmt = (
            select(
                TrainingRequest,
                Employee,
                Training,
                Domaine.nom_domaine,
            )
            .join(TrainingRequest.employee)
            .outerjoin(TrainingRequest.training)
            .outerjoin(Training.domaine)
            .where(
                TrainingRequest.status == TRAININGREQUESTSTATUS.PENDING.value,
                TrainingRequest.is_deleted.is_(False),
            )
        )

        return self.session.execute(stmt).all()
