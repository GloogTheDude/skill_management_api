from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from dto.skill_dto import QuerySkillDTO
from errors.domaine_errors import ErrorIDDomaineMissing
from errors.skill_errors import ErrorIDSkillMissing, ErrorSkillAlreadyDeleted
from models.domaine import Domaine
from models.skill import Skill
from sqlalchemy import inspect

class SkillRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        stmt = (
            select(Skill)
            .where(Skill.is_deleted.is_(False))
            .order_by(Skill.id_skill)
        )
        return self.session.scalars(stmt).all()

    def get_by_id(self, id_skill: int) -> Skill | None:
        return self.session.get(Skill, id_skill)

    def add(self, name_skill, id_domaine) -> Skill:
        stmt = select(Domaine).where(Domaine.id_domaine == id_domaine)
        domaine = self.session.scalar(stmt)
        if not domaine:
            raise ErrorIDDomaineMissing()
        skill = Skill(name_skill= name_skill, id_domaine=id_domaine)
        self.session.add(skill)
        self.session.flush()
        return skill

    def soft_delete(self, id_skill: int) -> None:
        skill = self.get_by_id(id_skill)
        if skill is None:
            raise ErrorIDSkillMissing()
        if skill.is_deleted:
            raise ErrorSkillAlreadyDeleted()
        skill.is_deleted = True

    def get_all_for_crud(self):
        stmt = (
            select(Skill.id_skill, Skill.name_skill, Domaine.nom_domaine)
            .outerjoin(Domaine, Domaine.id_domaine == Skill.id_domaine)
            .where(Skill.is_deleted.is_(False))
            .order_by(Skill.id_skill)
        )
        return self.session.execute(stmt).all()

    

    def update(self, skill_dto: QuerySkillDTO):
        skill = self.get_by_id(skill_dto.id_skill)
        stmt = (select(Domaine)
                .where(Domaine.id_domaine == skill_dto.id_domaine))
        domaine = self.session.scalar(stmt)
        if skill is None:
            raise ErrorIDSkillMissing()
        if domaine is None:
            raise ErrorIDDomaineMissing()

        state = inspect(skill)

        print("persistent:", state.persistent)
        print("detached:", state.detached)

        skill.name_skill = skill_dto.name_skill
        skill.id_domaine = skill_dto.id_domaine

        print("dirty:", self.session.dirty)

        return skill
