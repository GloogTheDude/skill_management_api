from dto.certification_dto import ResponseCertificationDTO


class CertificationMenu:
    @staticmethod
    def main_menu() -> int:
        user_choice = -1

        while not (0 <= user_choice <= 4):
            print("===== CERTIFICATION CRUD =====")
            print("1. List certifications")
            print("2. Create certification")
            print("3. Update certification")
            print("4. Delete certification")
            print("0. Leave")

            user_choice = int(input("Your choice: "))

        return user_choice

    @staticmethod
    def display_certifications(certifications: list[ResponseCertificationDTO]) -> None:
        print("===== CERTIFICATIONS =====")

        if not certifications:
            print("No certification found.")
            return

        for certification in certifications:
            domaine_name = certification.domaine_name or "No domain"
            validity = (
                f"{certification.validity_month} months"
                if certification.validity_month is not None
                else "No expiration"
            )

            print(
                f"{certification.id_certification}: "
                f"{certification.subject_certification} - "
                f"{domaine_name} - "
                f"{validity}"
            )

    @staticmethod
    def ask_id_certification() -> int:
        return int(input("Certification id: "))

    @staticmethod
    def ask_subject_certification() -> str:
        return input("Certification subject: ").strip()

    @staticmethod
    def ask_validity_month() -> int | None:
        raw_value = input("Validity in months, empty if no expiration: ").strip()

        if raw_value == "":
            return None

        return int(raw_value)

    @staticmethod
    def ask_id_domaine() -> int:
        return int(input("Domaine id: "))

    @staticmethod
    def display_success(message: str) -> None:
        print(message)

    @staticmethod
    def display_error(message: str) -> None:
        print(message)