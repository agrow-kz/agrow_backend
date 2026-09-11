from src.core.shared.domain.exceptions import (
    AccessDeniedError,
    AlreadyExistsError,
    NotFoundError,
)


class InsufficientPermissionsError(AccessDeniedError):
    def __init__(self):
        super().__init__(message="У вас недостаточно прав доступа")


class AdminAlreadyExistsError(AlreadyExistsError):
    def __init__(self):
        super().__init__(message="Такой администратор уже зарегистрирован")


class AdminNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(message="Администратор не найден")


class PermissionNotFoundError(NotFoundError):
    def __init__(self):
        super().__init__(message="Права не найдены")
