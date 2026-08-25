from dto.diploma_dto import ResponseDiplomaDTO
from models.diploma import Diploma


class DiplomaMenu:
    @staticmethod
    def main_menu() -> int:
        user_choice = -1

        while not (0 <= user_choice <= 4):
            print("===== DIPLOMA CRUD =====")
            print("1. List diplomas")
            print("2. Create diploma")
            print("3. Update diploma")
            print("4. Delete diploma")
            print("0. Leave")

            user_choice = int(input("Your choice: "))

        return user_choice

    @staticmethod
    def display_diplomas(diplomas: list[ResponseDiplomaDTO]) -> None:
        print("===== DIPLOMAS =====")

        if not diplomas:
            print("No diploma found.")
            return

        for diploma in diplomas:
            domaine_name = diploma.domaine_name or "No domain"

            print(
                f"{diploma.id_diploma}: "
                f"{diploma.subject_diploma} - "
                f"{diploma.level_diploma} - "
                f"{domaine_name}"
            )
            
    @staticmethod
    def ask_id_diploma() -> int:
        return int(input("Diploma id: "))

    @staticmethod
    def ask_subject_diploma() -> str:
        return input("Diploma subject: ").strip()

    @staticmethod
    def ask_level_diploma() -> str:
        return input("Diploma level: ").strip()

    @staticmethod
    def ask_id_domaine() -> int:
        return int(input("Domaine id: "))

    @staticmethod
    def display_success(message: str) -> None:
        print(message)

    @staticmethod
    def display_error(message: str) -> None:
        print(message)