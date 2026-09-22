from db.repositories.base_repository import BaseRepository
from models.training_skill import TrainingSkill

class TrainingSkillRepository(BaseRepository[TrainingSkill]):
    model= TrainingSkill
