from db.repositories.participation_repository import ParticipationRepository

from core.constants import PARTICIPATIONSTATUS,TYPEPARTICIPATIONDTO

from datetime import datetime

from models.training import Training
from models.participation import Participation
from models.employee import Employee

from dto.participation_dto import ParticipationDTO
from menus.participation_menu import ParticipationMenu as pm

class ParticipationService():
    
    def __init__(self, participation_repository:ParticipationRepository):
        self.participation_repository = participation_repository

    def get_participations_completable(self)->dict[int, ParticipationDTO]:
        rows = self.participation_repository.get_details_by_status(PARTICIPATIONSTATUS.IN_PROGRESS.value,min_end_date=datetime.today())
        i=1
        participations_completable = {}

        for row in rows:
            participation:Participation = row[0]
            employee:Employee = row[1]
            training:Training = row[2]

            participation_dto = ParticipationDTO(
                employee_id = employee.id_employee,
                employee_first_name = employee.first_name,
                employee_last_name = employee.last_name,
                training_id = training.id_training,
                training_title = training.title,
                training_start = training.start_,
                training_end = training.end_,
                participation_status = participation.status,
                training_type=None
            )
            if training.id_diploma:
                participation_dto.training_type = TYPEPARTICIPATIONDTO.DIPLOMA.value
            elif training.id_certification:
                participation_dto.training_type  = TYPEPARTICIPATIONDTO.CERTIFICATION.value
            else:
                participation_dto.training_type  = TYPEPARTICIPATIONDTO.SKILL.value

            participations_completable[i] = participation_dto
            i+=1

        return participations_completable
    
    def set_participation_to_completed(self, id_employee, id_training):
        self.participation_repository.change_status(id_employee, id_training, PARTICIPATIONSTATUS.COMPLETED.value)
        

    
   

