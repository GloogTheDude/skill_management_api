class TrainingRequestConflict(Exception):
    def __init__(self, detail: str):
        super().__init__(detail)


class TrainingRequestNotFound(Exception):
    def __init__(self, detail: str = "Training request not found."):
        super().__init__(detail)


class RelatedEntityNotFound(Exception):
    def __init__(self, entity_name: str):
        super().__init__(f"{entity_name} not found or is deleted.")


class ActiveParticipationConflict(Exception):
    def __init__(self):
        super().__init__(
            "A participation already exists for this employee and training."
        )
