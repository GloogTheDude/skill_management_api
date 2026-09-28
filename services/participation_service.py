from typing import Any

from sqlalchemy.exc import NoResultFound

from core.constants import TYPEPARTICIPATIONDTO
from dto.participation_crud_dto import (
    CompletableParticipationDTO,
    ParticipationListDTO,
    ResponseParticipationDTO,
)
from models.participation import Participation
from services.base_crud_service import BaseCrudService


class ParticipationService(BaseCrudService[Participation]):

    def _get_active(self, ident: Any) -> Participation:
        participation = self._get_entity_by_id(ident)
        if participation.is_deleted:
            raise NoResultFound()
        return participation

    def get_all(self, employee_id: int | None = None, access_level: int | None = None):
        if employee_id is not None and access_level is not None:
            return [
                ParticipationListDTO(
                    id_employee=participation.id_employee,
                    id_training=participation.id_training,
                    status=participation.status,
                    employee_first_name=first_name,
                    employee_last_name=last_name,
                    training_title=title,
                    domaine_name=domaine_name,
                    source_name=source_name,
                    location=location,
                    start_=start_,
                    end_=end_,
                    duration_hours=duration_hours,
                    cost_hour=cost_hour,
                )
                for (
                    participation, first_name, last_name, title, domaine_name,
                    source_name, location, start_, end_, duration_hours, cost_hour,
                ) in self.repository.get_for_scope(employee_id, access_level)
            ]
        participations = self._get_all_entities()
        return [
            ResponseParticipationDTO.from_entity(participation)
            for participation in participations
        ]

    def get_by_id(
        self,
        id_employee: int,
        id_training: int,
    ) -> ResponseParticipationDTO:
        participation = self._get_active((id_employee, id_training))
        return ResponseParticipationDTO.from_entity(participation)

    def get_completable(self) -> list[CompletableParticipationDTO]:
        rows = self.repository.get_completable()
        result = []

        for participation, employee, training in rows:
            if training.id_diploma:
                training_type = TYPEPARTICIPATIONDTO.DIPLOMA.value
            elif training.id_certification:
                training_type = TYPEPARTICIPATIONDTO.CERTIFICATION.value
            else:
                training_type = TYPEPARTICIPATIONDTO.SKILL.value

            result.append(
                CompletableParticipationDTO(
                    id_employee=employee.id_employee,
                    employee_first_name=employee.first_name,
                    employee_last_name=employee.last_name,
                    id_training=training.id_training,
                    training_title=training.title,
                    training_start=training.start_,
                    training_end=training.end_,
                    participation_status=participation.status,
                    training_type=training_type,
                )
            )

        return result
