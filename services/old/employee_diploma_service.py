from db.repositories.employee_diploma_repository import EmployeeDiplomaRepository
from models.employee_diploma import EmployeeDiploma
from datetime import date


class EmployeeDiplomaService():
    def __init__(self, employee_diploma_repository:EmployeeDiplomaRepository):
        self.employee_diploma_repository = employee_diploma_repository
        
    def add(self, employee_id:int, diploma_id:int, start_:date, end_:date, distinction:str, school:str):
        employee_diploma = EmployeeDiploma()
        employee_diploma.id_diploma = diploma_id
        employee_diploma.id_employee = employee_id
        employee_diploma.start_ = start_
        employee_diploma.end_ = end_
        employee_diploma.school = school
        employee_diploma.distinction = distinction
        employee_diploma.doc = None
        employee_diploma.is_deleted = False

        self.employee_diploma_repository.add(employee_diploma)
