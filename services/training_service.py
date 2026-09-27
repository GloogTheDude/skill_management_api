
from dto.training_dto import UpdateTrainingDTO, CreateTrainingDTO, ResponseTrainingDTO
from models.training import Training
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_source_repository import TrainingSourceRepository


class TrainingService(BaseCrudService[Training]):
    def __init__(
        self,
        repository,
        domaine_repository: DomaineRepository | None = None,
        source_repository: TrainingSourceRepository | None = None,
    ):
        super().__init__(repository)
        self.domaine_repository = domaine_repository
        self.source_repository = source_repository

    def _validate_domaine(self, id_domaine):
        if self.domaine_repository is not None:
            if self.domaine_repository.get_one(id_domaine).is_deleted:
                raise NoResultFound()

    def _validate_source(self, id_source):
        if self.source_repository is not None:
            if self.source_repository.get_one(id_source).is_deleted:
                raise NoResultFound()

    @staticmethod
    def _validate_targets(id_diploma, id_certification):
        if id_diploma is not None and id_certification is not None:
            raise ValueError("A training cannot have both a diploma and a certification.")
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
        self._validate_domaine(dto.id_domaine)
        self._validate_source(dto.id_source)
        self._validate_targets(dto.id_diploma, dto.id_certification)
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
        training = self.repository.get_one(id_training)
        if "id_domaine" in data:
            self._validate_domaine(data["id_domaine"])
        if "id_source" in data:
            self._validate_source(data["id_source"])
        self._validate_targets(
            data.get("id_diploma", training.id_diploma),
            data.get("id_certification", training.id_certification),
        )
        training = self.repository.update(
            id_training,
            **data
        )

        return ResponseTrainingDTO.from_entity(training)
