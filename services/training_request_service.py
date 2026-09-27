from datetime import date

from sqlalchemy.exc import NoResultFound

from dto.training_request_api_dto import (
    CreatePersonalizedTrainingRequestDTO,
    CreatePlannedTrainingRequestDTO,
    ResponseTrainingRequestDTO,
)
from db.repositories.training_request_repository import TrainingRequestRepository
from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from models.training_request import TrainingRequest
from errors.training_request_errors import RelatedEntityNotFound, TrainingRequestNotFound
from core.constants import TRAININGREQUESTSTATUS
from dto.auth_dto import AuthEmployeeDTO


class TrainingRequestService:
    def __init__(
        self,
        repository: TrainingRequestRepository,
        employee_repository: EmployeeRepository | None = None,
        training_repository: TrainingRepository | None = None,
    ):
        self.repository = repository
        self.employee_repository = employee_repository
        self.training_repository = training_repository

    def get_all(self) -> list[ResponseTrainingRequestDTO]:
        return [self._to_response(*row) for row in self.repository.get_all_with_details()]

    def get_mine(self, current_employee: AuthEmployeeDTO) -> list[ResponseTrainingRequestDTO]:
        return [
            self._to_response(*row)
            for row in self.repository.get_for_employee(current_employee.id_employee)
        ]

    def get_by_id(self, id_request: int) -> ResponseTrainingRequestDTO:
        row = self.repository.get_by_id_with_details(id_request)
        if row is None or row[0].is_deleted:
            raise TrainingRequestNotFound()
        return self._to_response(*row)

    def create_planned(
        self,
        dto: CreatePlannedTrainingRequestDTO,
    ) -> ResponseTrainingRequestDTO:
        request = self._new_request(
            id_employee=dto.id_employee,
            id_training=dto.id_training,
        )
        self._validate_related_entities(
            dto.id_employee,
            dto.id_training,
        )
        self.repository.add(request)
        return self._response_after_flush(request)

    def create_personalized(
        self,
        dto: CreatePersonalizedTrainingRequestDTO,
    ) -> ResponseTrainingRequestDTO:
        request = self._new_request(
            id_employee=dto.id_employee,
            request_desc=dto.request_desc,
        )
        self._validate_related_entities(dto.id_employee, None)
        self.repository.add(request)
        return self._response_after_flush(request)

    def _validate_related_entities(
        self,
        id_employee: int,
        id_training: int | None,
    ) -> None:
        if self.employee_repository is not None:
            try:
                employee = self.employee_repository.get_one(id_employee)
            except NoResultFound as exc:
                raise RelatedEntityNotFound("Employee") from exc
            if employee.is_deleted:
                raise RelatedEntityNotFound("Employee")

        if id_training is not None and self.training_repository is not None:
            try:
                training = self.training_repository.get_one(id_training)
            except NoResultFound as exc:
                raise RelatedEntityNotFound("Training") from exc
            if training.is_deleted:
                raise RelatedEntityNotFound("Training")

    def _response_after_flush(self, request: TrainingRequest):
        row = self.repository.get_by_id_with_details(request.id_training_request)
        return self._to_response(*row)

    @staticmethod
    def _new_request(
        *,
        id_employee: int,
        id_training: int | None = None,
        request_desc: str | None = None,
    ) -> TrainingRequest:
        return TrainingRequest(
            id_employee=id_employee,
            id_training=id_training,
            request_desc=request_desc,
            status=TRAININGREQUESTSTATUS.PENDING.value,
            reason=None,
            requested_at=date.today(),
            id_validator=None,
            is_deleted=False,
        )

    @staticmethod
    def _to_response(
        request: TrainingRequest,
        training_title: str | None,
        domaine_name: str | None,
    ) -> ResponseTrainingRequestDTO:
        return ResponseTrainingRequestDTO(
            id_training_request=request.id_training_request,
            request_desc=request.request_desc,
            status=request.status,
            reason=request.reason,
            requested_at=request.requested_at,
            is_deleted=request.is_deleted,
            id_employee=request.id_employee,
            id_training=request.id_training,
            id_validator=request.id_validator,
            training_title=training_title,
            domaine_name=domaine_name,
        )
