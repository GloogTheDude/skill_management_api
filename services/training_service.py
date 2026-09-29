
from dto.training_dto import UpdateTrainingDTO, CreateTrainingDTO, ResponseTrainingDTO
from models.training import Training
from services.base_crud_service import BaseCrudService
from sqlalchemy.exc import NoResultFound
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.training_source_repository import TrainingSourceRepository
from services.training_support_service import TrainingSupportService
from errors.training_errors import TrainingLifecycleConflict


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
        if hasattr(self.repository, "get_all_with_usage"):
            return [
                ResponseTrainingDTO.from_entity(training, is_used)
                for training, is_used in self.repository.get_all_with_usage()
            ]
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
        if dto.start_ > dto.end_:
            raise ValueError("Training start date must be before or equal to its end date.")
        requested = [(item.id_skill, item.level) for item in dto.skills]
        session = getattr(self.repository, "_session", None)
        if session is None:
            if dto.id_diploma is None and dto.id_certification is None and not requested:
                raise ValueError("A training must have a diploma, certification, or skill.")
            support = None
        else:
            support = TrainingSupportService(session)
            support.validate_support(dto.id_diploma, dto.id_certification, [item.id_skill for item in dto.skills])
        training = Training(
            title=dto.title,
            id_domaine=dto.id_domaine,
            id_source=dto.id_source,
            location=dto.location,
            id_certification=dto.id_certification,
            id_diploma=dto.id_diploma,
            start_=dto.start_,
            end_=dto.end_,
            cost_hour=dto.cost_hour,
            duration_hours=dto.duration_hours
        )
        created = self.repository.add(training)
        if requested and support is not None:
            support.replace_skills(created.id_training, requested)
        return ResponseTrainingDTO.from_entity(created)

    def update(self,id_training: int,dto: UpdateTrainingDTO) -> ResponseTrainingDTO:
        data = dto.model_dump(exclude_unset=True)
        training = self.repository.get_one(id_training)
        session = getattr(self.repository, "_session", None)
        support = TrainingSupportService(session) if session is not None else None
        if support is not None and support.is_used(id_training):
            allowed = {"title", "location"}
            immutable = set(data) - allowed
            if immutable:
                fields = ", ".join(sorted(immutable))
                raise TrainingLifecycleConflict(
                    f"Used training fields cannot be changed: {fields}."
                )
        if "id_domaine" in data:
            self._validate_domaine(data["id_domaine"])
        if "id_source" in data:
            self._validate_source(data["id_source"])
        self._validate_targets(
            data.get("id_diploma", training.id_diploma),
            data.get("id_certification", training.id_certification),
        )
        final_diploma = data.get("id_diploma", training.id_diploma)
        final_certification = data.get("id_certification", training.id_certification)
        final_start = data.get("start_", training.start_)
        final_end = data.get("end_", training.end_)
        if final_start is not None and final_end is not None and final_start > final_end:
            raise ValueError("Training start date must be before or equal to its end date.")
        support_changed = (
            "skills" in data
            or "id_diploma" in data
            or "id_certification" in data
        )
        if not support_changed:
            requested = None
            support = None
        elif "skills" in data:
            requested = data.pop("skills") or []
            if support is not None:
                support.validate_final_state(
                    id_training,
                    final_diploma,
                    final_certification,
                    [item["id_skill"] for item in requested],
                )
            elif final_diploma is None and final_certification is None and not requested:
                raise ValueError("A training must have a diploma, certification, or skill.")
        else:
            requested = None
            if support is not None:
                support.validate_final_state(id_training, final_diploma, final_certification)
            elif final_diploma is None and final_certification is None:
                raise ValueError("A training must have a diploma, certification, or skill.")
        training = self.repository.update(
            id_training,
            **data
        )

        if requested is not None and support is not None:
            support.replace_skills(
                id_training,
                [(item["id_skill"], item["level"]) for item in requested],
            )

        return ResponseTrainingDTO.from_entity(training)
