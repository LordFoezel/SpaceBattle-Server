from app.core.errors import AppErrorCode, AppHttpStatus

class AppError(Exception):
    status: AppHttpStatus = AppHttpStatus.INTERNAL
    code: AppErrorCode = AppErrorCode.INTERNAL
    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details

# 4xx – Clientfehler
class BadRequestError(AppError):
    status = AppHttpStatus.BAD_REQUEST
    code = AppErrorCode.BAD_REQUEST

class ValidationError(AppError):
    status = AppHttpStatus.UNPROCESSABLE_ENTITY
    code = AppErrorCode.VALIDATION

class UnauthorizedError(AppError):
    status = AppHttpStatus.UNAUTHORIZED
    code = AppErrorCode.UNAUTHORIZED

class ForbiddenError(AppError):
    status = AppHttpStatus.FORBIDDEN
    code = AppErrorCode.FORBIDDEN

class NotFoundError(AppError):
    status = AppHttpStatus.NOT_FOUND
    code = AppErrorCode.NOT_FOUND

class MethodNotAllowedError(AppError):
    status = AppHttpStatus.METHOD_NOT_ALLOWED
    code = AppErrorCode.METHOD_NOT_ALLOWED

class ConflictError(AppError):
    status = AppHttpStatus.CONFLICT
    code = AppErrorCode.CONFLICT

class AlreadyExistsError(AppError):
    status = AppHttpStatus.CONFLICT
    code = AppErrorCode.ALREADY_EXISTS

class PreconditionFailedError(AppError):
    status = AppHttpStatus.PRECONDITION_FAILED
    code = AppErrorCode.PRECONDITION_FAILED

class PayloadTooLargeError(AppError):
    status = AppHttpStatus.PAYLOAD_TOO_LARGE
    code = AppErrorCode.PAYLOAD_TOO_LARGE

class UnsupportedMediaTypeError(AppError):
    status = AppHttpStatus.UNSUPPORTED_MEDIA
    code = AppErrorCode.UNSUPPORTED_MEDIA

class GoneError(AppError):
    status = AppHttpStatus.GONE
    code = AppErrorCode.NOT_FOUND  # oder eigener Code, wenn gewünscht

class RateLimitedError(AppError):
    status = AppHttpStatus.TOO_MANY_REQUESTS
    code = AppErrorCode.RATE_LIMITED

# 5xx – Serverfehler
class DependencyFailedError(AppError):
    status = AppHttpStatus.SERVICE_UNAVAILABLE
    code = AppErrorCode.DEPENDENCY_FAILED

class TimeoutError_(AppError):  # Name nicht mit builtins.TimeoutError kollidieren
    status = AppHttpStatus.GATEWAY_TIMEOUT
    code = AppErrorCode.TIMEOUT

class InternalServerError(AppError):
    status = AppHttpStatus.INTERNAL
    code = AppErrorCode.INTERNAL

class NotImplementedError_(AppError):  # nicht mit builtins.NotImplementedError kollidieren
    status = AppHttpStatus.NOT_IMPLEMENTED
    code = AppErrorCode.NOT_IMPLEMENTED

class BadGatewayError(AppError):
    status = AppHttpStatus.BAD_GATEWAY
    code = AppErrorCode.DEPENDENCY_FAILED

class ServiceUnavailableError(AppError):
    status = AppHttpStatus.SERVICE_UNAVAILABLE
    code = AppErrorCode.UNAVAILABLE

class GatewayTimeoutError(AppError):
    status = AppHttpStatus.GATEWAY_TIMEOUT
    code = AppErrorCode.TIMEOUT
