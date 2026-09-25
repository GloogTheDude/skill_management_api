from db.repositories.base_repository import BaseRepository
from models.skill_validation import SkillValidation


class SkillValidationRepository(BaseRepository[SkillValidation]):
    model = SkillValidation
