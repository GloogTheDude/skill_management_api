class AuthorizationForbidden(Exception):
    def __init__(self, detail: str = "You are not authorized to process this request."):
        super().__init__(detail)
