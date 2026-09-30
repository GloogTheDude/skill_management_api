class ParticipationInvalidStatus(Exception):
    def __init__(self, status: str):
        super().__init__(
            f"Participation cannot be completed from status {status}."
        )


class ParticipationCannotCancel(Exception):
    def __init__(self, message="Participation cannot be cancelled after the training has ended."):
        super().__init__(message)


class TrainingNotCompleted(Exception):
    def __init__(self):
        super().__init__(
            "Training has no end date or has not been completed yet."
        )
