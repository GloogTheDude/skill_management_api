from models.diploma_skill import DiplomaSkill


def replace_skills(self, id_diploma: int, skill_levels: list[tuple[int, int]]) -> bool:
    diploma = self.diploma_repository.get_by_id(id_diploma)

    if diploma is None or diploma.is_deleted:
        return False

    self.diploma_skill_repository.soft_delete_by_diploma_id(id_diploma)

    for id_skill, min_level in skill_levels:
        link = DiplomaSkill()
        link.id_diploma = id_diploma
        link.id_skill = id_skill
        link.min_level = min_level
        link.is_deleted = False
        self.diploma_skill_repository.add(link)

    return True