
from datetime import date
from dateutil.relativedelta import relativedelta

from core.constants import CERTIFICATIONSTATUS
from db.repositories.employee_certification_repository import EmployeeCertificationRepository
from dto.employee_certification_dto import CloseToExpirationDTO
from models.certification import Certification
from models.employee_certification import EmployeeCertification

class EmployeeCertificationService():
    def __init__(self, employee_certification_repository: EmployeeCertificationRepository):
        self.employee_certification_repository = employee_certification_repository
    
    def add(self,id_employee:int, id_certification:int, start_:date, end_:date, organism:str, 
            validity_month:int, evaluation:str = None):
        employee_certification = EmployeeCertification()
        employee_certification.id_employee = id_employee
        employee_certification.id_certification = id_certification
        employee_certification.start_ = start_
        employee_certification.end_ = end_
        employee_certification.is_deleted = False
        employee_certification.organism = organism
        employee_certification.evaluation = evaluation
        if validity_month is None or end_ is None: 
            employee_certification.expiration =None
        else: 
            employee_certification.expiration = end_ + relativedelta(months=validity_month)
        self.employee_certification_repository.add(employee_certification)

    def get_close_to_expiration(self)->list[CloseToExpirationDTO]:
        today = date.today()
        close_to_expiration = self.employee_certification_repository.get_close_to_expiration()
        arr_dto = []
        for employee_certification, employee, certification in close_to_expiration:
            dto = CloseToExpirationDTO(
                employee_id = employee.id_employee,
                employee_first_name = employee.first_name,
                employee_last_name= employee.last_name,
                certification_id = certification.id_certification,
                certification_name = certification.subject_certification,
                expiration_date = employee_certification.expiration,
                status = None
            )
            if dto.expiration_date < today:
                dto.status = CERTIFICATIONSTATUS.EXPIRED.value
            elif dto.expiration_date <= today + relativedelta(months=1):
                dto.status = CERTIFICATIONSTATUS.URGENT.value
            else:
                dto.status = CERTIFICATIONSTATUS.EXPIRING_SOON.value
            arr_dto.append(dto)
        return arr_dto