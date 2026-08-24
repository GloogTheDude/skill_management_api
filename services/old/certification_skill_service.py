from models.certification_skill import CertificationSkill


def replace_skills(self, id_certification: int, skill_levels: list[tuple[int, int]]) -> bool:
    certification = self.certification_repository.get_by_id(id_certification)

    if certification is None or certification.is_deleted:
        return False

    self.certification_skill_repository.soft_delete_by_certification_id(id_certification)

    for id_skill, granted_level in skill_levels:
        link = CertificationSkill()
        link.id_certification = id_certification
        link.id_skill = id_skill
        link.granted_level = granted_level
        link.is_deleted = False
        self.certification_skill_repository.add(link)

    return True