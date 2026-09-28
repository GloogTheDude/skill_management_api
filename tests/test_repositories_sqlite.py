import unittest
from datetime import date

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from db.repositories.employee_repository import EmployeeRepository
from db.repositories.training_repository import TrainingRepository
from db.repositories.training_request_repository import TrainingRequestRepository
from models import Base, Role, Employee, Domaine, Training, TrainingRequest,AccessLevel


class RepositorySQLiteTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.seed()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def seed(self):
        self.session.add_all([
            AccessLevel(id_access_level=1, label="Employee", level=1),
            AccessLevel(id_access_level=2, label="Manager", level=2),
            AccessLevel(id_access_level=3, label="HR", level=3),
            Role(id_role=1, denomination_role="Employee"),
            Role(id_role=2, denomination_role="Manager"),
            Domaine(id_domaine=1, nom_domaine="Backend", is_deleted=False),
            Domaine(id_domaine=2, nom_domaine="Database", is_deleted=False),
            Domaine(id_domaine=3, nom_domaine="Deleted Domaine", is_deleted=True),
            Employee(id_employee=1, first_name="Manager", last_name="One", hash_password="hash", mail="manager@company.be", id_role=2, id_manager=None, is_deleted=False),
            Employee(id_employee=4, first_name="David", last_name="Henrichmann", hash_password="hash", mail="david@company.be", id_role=1, id_manager=1, is_deleted=False),
            Employee(id_employee=5, first_name="Nora", last_name="Simon", hash_password="hash", mail="nora@company.be", id_role=1, id_manager=1, is_deleted=False),
            Training(id_training=1, title="Already requested", id_domaine=1, start_=date(2099, 1, 1), end_=date(2099, 1, 2), is_deleted=False),
            Training(id_training=2, title="Available future", id_domaine=2, start_=date(2099, 2, 1), end_=date(2099, 2, 2), is_deleted=False),
            Training(id_training=3, title="Past training", id_domaine=1, start_=date(2000, 1, 1), end_=date(2000, 1, 2), is_deleted=False),
            Training(id_training=4, title="Deleted training", id_domaine=1, start_=date(2099, 3, 1), end_=date(2099, 3, 2), is_deleted=True),
            Training(id_training=5, title="Deleted domaine training", id_domaine=3, start_=date(2099, 4, 1), end_=date(2099, 4, 2), is_deleted=False),
            TrainingRequest(id_training_request=1, request_desc=None, status="PENDING", reason=None, requested_at=date(2026, 1, 1), is_deleted=False, id_employee=4, id_training=1, id_validator=1),
            TrainingRequest(id_training_request=2, request_desc="Personalised request", status="PENDING", reason=None, requested_at=date(2026, 1, 2), is_deleted=False, id_employee=4, id_training=None, id_validator=None),
        ])
        self.session.commit()

    def test_employee_repository_basic_queries(self):
        repo = EmployeeRepository(self.session)

        self.assertEqual(repo.get_active_by_id(4).first_name, "David")
        self.assertIsNone(repo.get_active_by_id(999))
        self.assertEqual(repo.get_active_by_mail("david@company.be").id_employee, 4)
        self.assertIsNone(repo.get_active_by_mail("missing@company.be"))
        self.assertEqual({e.id_employee for e in repo.get_all()}, {1, 4, 5})

    def test_employee_repository_save_and_delete(self):
        repo = EmployeeRepository(self.session)
        employee = Employee(first_name="Test", last_name="User", hash_password="hash", mail="test@company.be", id_role=1, id_manager=1, is_deleted=False)

        repo.add(employee)
        self.session.flush()
        self.assertIsNotNone(employee.id_employee)
        self.assertEqual(repo.get_active_by_mail("test@company.be").first_name, "Test")

        repo.delete(employee.id_employee)
        self.assertIsNone(repo.get_active_by_mail("test@company.be"))

    def test_training_repository_excludes_requested_past_deleted_and_deleted_domaines(self):
        repo = TrainingRepository(self.session)

        rows = repo.get_available_for_employee(id_employee=4)
        titles = {training.title for training, domaine_name in rows}

        self.assertEqual(titles, {"Available future"})

    def test_training_request_repository_returns_employee_preplanned_requests(self):
        repo = TrainingRequestRepository(self.session)

        rows = repo.get_for_employee(id_employee=4)
        rows_by_id = {tr.id_training_request: (tr, title, domaine_name) for tr, title, domaine_name in rows}

        self.assertIn(1, rows_by_id)
        self.assertEqual(rows_by_id[1][1], "Already requested")
        self.assertEqual(rows_by_id[1][2], "Backend")

    def test_training_request_repository_should_also_return_personalised_requests(self):
        """Current implementation uses inner joins, so requests with id_training=None are lost."""
        repo = TrainingRequestRepository(self.session)

        rows = repo.get_for_employee(id_employee=4)
        ids = {tr.id_training_request for tr, title, domaine_name in rows}

        self.assertIn(2, ids)


if __name__ == "__main__":
    unittest.main()
