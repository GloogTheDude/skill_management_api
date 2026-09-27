from core.constants import PARTICIPATIONSTATUS, TRAININGREQUESTSTATUS
from sqlalchemy.exc import NoResultFound
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.participation_repository import ParticipationRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_request_repository import TrainingRequestRepository
from dto.training_request_api_dto import (
    ApproveTrainingRequestDTO,
    RejectTrainingRequestDTO,
    ResponseTrainingRequestDTO,
)
from dto.auth_dto import AuthEmployeeDTO
from errors.training_request_errors import (
    ActiveParticipationConflict,
    RelatedEntityNotFound,
    TrainingRequestConflict,
    TrainingRequestNotFound,
    TrainingRequestForbidden,
)
from models.participation import Participation
from services.training_request_service import TrainingRequestService
from services.training_request_authorization import TrainingRequestAuthorization


class TrainingRequestWorkflowService:
    def __init__(
        self,
        training_request_repository: TrainingRequestRepository,
        employee_repository: EmployeeRepository,
        training_repository: TrainingRepository,
        participation_repository: ParticipationRepository,
    ):
        self.training_request_repository = training_request_repository
        self.employee_repository = employee_repository
        self.training_repository = training_repository
        self.participation_repository = participation_repository

    def approve(
        self,
        id_request: int,
        dto: ApproveTrainingRequestDTO,
        current_employee: AuthEmployeeDTO,
    ) -> ResponseTrainingRequestDTO:
        request = self._get_pending_request(id_request)

        try:
            employee = self.employee_repository.get_one(request.id_employee)
        except NoResultFound as exc:
            raise RelatedEntityNotFound("Employee") from exc
        if employee.is_deleted:
            raise RelatedEntityNotFound("Employee")

        TrainingRequestAuthorization.authorize_action(current_employee, employee)

        if request.id_training is not None:
            if dto.id_training is not None:
                raise TrainingRequestConflict(
                    "A planned request cannot receive another training."
                )
            id_training = request.id_training
        else:
            if dto.id_training is None:
                raise TrainingRequestConflict(
                    "A personalized request must be linked to a training."
                )
            id_training = dto.id_training

        try:
            training = self.training_repository.get_one(id_training)
        except NoResultFound as exc:
            raise RelatedEntityNotFound("Training") from exc
        if training.is_deleted:
            raise RelatedEntityNotFound("Training")

        existing = self.participation_repository.get_existing(
            request.id_employee,
            id_training,
        )
        if existing is not None:
            raise ActiveParticipationConflict()

        request.status = TRAININGREQUESTSTATUS.VALIDATED.value
        request.id_validator = current_employee.id_employee
        request.id_training = id_training
        request.reason = None
        self.training_request_repository.session.flush()

        self.participation_repository.add(
            Participation(
                id_employee=request.id_employee,
                id_training=id_training,
                status=PARTICIPATIONSTATUS.REGISTERED.value,
                is_deleted=False,
            )
        )

        return TrainingRequestService._to_response(
            request,
            training.title,
            training.domaine.nom_domaine if training.domaine else None,
        )

    def reject(
        self,
        id_request: int,
        dto: RejectTrainingRequestDTO,
        current_employee: AuthEmployeeDTO,
    ) -> ResponseTrainingRequestDTO:
        request = self._get_pending_request(id_request)

        try:
            employee = self.employee_repository.get_one(request.id_employee)
        except NoResultFound as exc:
            raise RelatedEntityNotFound("Employee") from exc
        if employee.is_deleted:
            raise RelatedEntityNotFound("Employee")

        TrainingRequestAuthorization.authorize_action(current_employee, employee)

        request.status = TRAININGREQUESTSTATUS.REFUSED.value
        request.id_validator = current_employee.id_employee
        request.reason = dto.reason
        self.training_request_repository.session.flush()

        row = self.training_request_repository.get_by_id_with_details(id_request)
        return TrainingRequestService._to_response(*row)

    def _get_pending_request(self, id_request: int):
        request = self.training_request_repository.get_active_by_id(id_request)
        if request is None:
            raise TrainingRequestNotFound()
        if request.status != TRAININGREQUESTSTATUS.PENDING.value:
            raise TrainingRequestConflict("Training request has already been processed.")
        return request
