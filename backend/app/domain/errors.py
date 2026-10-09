class DomainError(Exception):
    pass


class InvalidCredentials(DomainError):
    pass


class InvalidToken(DomainError):
    pass


class PermissionDenied(DomainError):
    pass


class TooManyAttempts(DomainError):
    pass
