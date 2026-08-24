from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from db.repositories.base_repository import BaseRepository
from dto.skill_dto import QuerySkillDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from errors.skill_errors import ErrorIDSkillMissing, ErrorSkillAlreadyDeleted
from models.domaine import Domaine
from models.skill import Skill
from sqlalchemy import inspect

class SkillRepository(BaseRepository[Skill]):
    model = Skill