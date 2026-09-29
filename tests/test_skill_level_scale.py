import pytest
from pydantic import ValidationError

from dto.certification_skill_dto import CreateCertificationSkillDTO
from dto.diploma_skill_dto import CreateDiplomaSkillDTO
from dto.skill_validation_dto import CreateSkillValidationDTO
from dto.training_skill_dto import CreateTrainingSkillDTO


@pytest.mark.parametrize("level", [1, 5])
def test_skill_level_scale_accepts_bounds(level):
    assert CreateSkillValidationDTO(
        id_validation=1, id_employee=1, id_skill=1, level_skill=level
    ).level_skill == level
    assert CreateTrainingSkillDTO(
        id_training=1, id_skill=1, granted_level=level
    ).granted_level == level
    assert CreateCertificationSkillDTO(
        id_certification=1, id_skill=1, granted_level=level
    ).granted_level == level
    assert CreateDiplomaSkillDTO(
        id_diploma=1, id_skill=1, min_level=level
    ).min_level == level


@pytest.mark.parametrize("level", [0, 6, 999, -1])
def test_skill_level_scale_rejects_out_of_range_values(level):
    for factory in (
        lambda: CreateSkillValidationDTO(
            id_validation=1, id_employee=1, id_skill=1, level_skill=level
        ),
        lambda: CreateTrainingSkillDTO(
            id_training=1, id_skill=1, granted_level=level
        ),
        lambda: CreateCertificationSkillDTO(
            id_certification=1, id_skill=1, granted_level=level
        ),
        lambda: CreateDiplomaSkillDTO(
            id_diploma=1, id_skill=1, min_level=level
        ),
    ):
        with pytest.raises(ValidationError):
            factory()
