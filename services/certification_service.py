from db.repositories.certification_repository import CertificationRepository
from db.repositories.domaine_repository import DomaineRepository
from db.repositories.certification_skill_repository import CertificationSkillRepository
from dto.certification_dto import QueryCertificationDTO, ResponseCertificationDTO
from dto.employee_skill_dto import EmployeeSkillDTO
from dto.employee_certification_dto import EmployeeCertificationDTO
from models.certification import Certification
from models.certification_skill import CertificationSkill
from services.base_crud_service import BaseCrudService


class CertificationService(BaseCrudService[Certification]):
    model=Certification

    def get_all(self)->list[ResponseCertificationDTO]:
        certifications = self._get_all_entities()
        return[
            ResponseCertificationDTO.from_entity(certification)
            for certification in certifications
        ]

    def get_by_id(self, id_certif:int)->ResponseCertificationDTO:
        certif = self._get_entity_by_id(id_certif)
        return ResponseCertificationDTO.from_entity(certif)

    def create(self, subject_certification:str, validity_month:int, id_domaine):
        certification = Certification(subject_certification = subject_certification,
                                      validity_month=  validity_month,
                                      id_domaine = id_domaine) 
        return ResponseCertificationDTO.from_entity(self.repository.add(certification))

    def update(self,dto: QueryCertificationDTO)->ResponseCertificationDTO:
        certification=self.repository.update(dto.id_certification,
                                             subject_certification=dto.subject_certification,
                                             validity_month=dto.validity_month,
                                             id_domaine=dto.id_domaine)
        return ResponseCertificationDTO.from_entity(certification)
        