from dto.certification_dto import CreateCertificationDTO,UpdateCertificationDTO, ResponseCertificationDTO
from models.certification import Certification
from services.base_crud_service import BaseCrudService


class CertificationService(BaseCrudService[Certification]):

    def get_all(self)->list[ResponseCertificationDTO]:
        certifications = self._get_all_entities()
        return[
            ResponseCertificationDTO.from_entity(certification)
            for certification in certifications
        ]

    def get_by_id(self, id_certification:int)->ResponseCertificationDTO:
        certif = self._get_entity_by_id(id_certification)
        return ResponseCertificationDTO.from_entity(certif)

    def create(
        self,
        dto: CreateCertificationDTO,
    ) -> ResponseCertificationDTO:
        certification = Certification(subject_certification = dto.subject_certification,
                                      validity_month=  dto.validity_month,
                                      id_domaine = dto.id_domaine) 
        return ResponseCertificationDTO.from_entity(self.repository.add(certification))

    def update(self,id_certification,dto: UpdateCertificationDTO)->ResponseCertificationDTO:
        data = dto.model_dump(exclude_unset=True)
        certification=self.repository.update(id_certification,
                                             **data)
        return ResponseCertificationDTO.from_entity(certification)
        