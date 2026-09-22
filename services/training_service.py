
from dto.training_dto import UpdateTrainingDTO, CreateTrainingDTO, ResponseTrainingDTO
from models.training import Training
from services.base_crud_service import BaseCrudService


class TrainingService(BaseCrudService[Training]):
    def get_all(self)->list[ResponseTrainingDTO]:
        trainings = self._get_all_entities()
        return[
            ResponseTrainingDTO.from_entity(training)
            for training in trainings
        ]

    def get_by_id(self, id_training)->ResponseTrainingDTO:
        training = self._get_entity_by_id(id_training)
        return ResponseTrainingDTO.from_entity(training)

    def create(self,dto:CreateTrainingDTO)->ResponseTrainingDTO:
        training = Training(
            title=dto.title,
            id_domaine=dto.id_domaine,
            id_source=dto.id_source,
            id_certification=dto.id_certification,
            id_diploma=dto.id_diploma,
            start_=dto.start_,
            end_=dto.end_,
            cost_hour=dto.cost_hour,
            duration_hours=dto.duration_hours
        )
        return ResponseTrainingDTO.from_entity(self.repository.add(training)) 

    def update(self,id_training: int,dto: UpdateTrainingDTO) -> ResponseTrainingDTO:
        data = dto.model_dump(exclude_unset=True)
        training = self.repository.update(
            id_training,
            **data
        )

        return ResponseTrainingDTO.from_entity(training)

    