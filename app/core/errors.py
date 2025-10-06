from enum import IntEnum, StrEnum
from pydantic import BaseModel
from typing import Any

class AppErrorCode(StrEnum):
    # Client-Fehler
    BAD_REQUEST          = "BAD_REQUEST"           # allgemeiner Request-Fehler
    VALIDATION           = "VALIDATION"            # Schema-/Feldvalidierung
    UNAUTHORIZED         = "UNAUTHORIZED"          # nicht eingeloggt/Token fehlt
    USER_NOT_VALIDATED   = "USER_NOT_VALIDATED"    # Benutzerkonto nicht verifiziert
    USER_BLOCKED         = "USER_BLOCKED"          # User is Blocked 
    FORBIDDEN            = "FORBIDDEN"             # keine Berechtigung
    NOT_FOUND            = "NOT_FOUND"             # Ressource fehlt
    METHOD_NOT_ALLOWED   = "METHOD_NOT_ALLOWED"
    CONFLICT             = "CONFLICT"              # Konflikt, z. B. Duplikat
    ALREADY_EXISTS       = "ALREADY_EXISTS"        # expliziter Duplikat-Fall
    PRECONDITION_FAILED  = "PRECONDITION_FAILED"
    UNSUPPORTED_MEDIA    = "UNSUPPORTED_MEDIA_TYPE"
    PAYLOAD_TOO_LARGE    = "PAYLOAD_TOO_LARGE"
    RATE_LIMITED         = "RATE_LIMITED"          # 429
    TIMEOUT              = "TIMEOUT"               # z. B. Upstream/DB Timeout

    # Server-Fehler
    DEPENDENCY_FAILED    = "DEPENDENCY_FAILED"     # z. B. DB/Mail down
    INTERNAL             = "INTERNAL"              # unerwarteter Fehler
    NOT_IMPLEMENTED      = "NOT_IMPLEMENTED"
    UNAVAILABLE          = "UNAVAILABLE"           # Wartung/Down

class AppHttpStatus(IntEnum):
    # 2xx
    OK                   = 200
    CREATED              = 201
    ACCEPTED             = 202
    NO_CONTENT           = 204

    # 4xx
    BAD_REQUEST          = 400
    UNAUTHORIZED         = 401
    FORBIDDEN            = 403
    NOT_FOUND            = 404
    METHOD_NOT_ALLOWED   = 405
    CONFLICT             = 409
    GONE                 = 410
    PRECONDITION_FAILED  = 412,
    PAYLOAD_TOO_LARGE    = 413
    UNSUPPORTED_MEDIA    = 415
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS    = 429

    # 5xx
    INTERNAL             = 500
    NOT_IMPLEMENTED      = 501
    BAD_GATEWAY          = 502
    SERVICE_UNAVAILABLE  = 503
    GATEWAY_TIMEOUT      = 504

class ErrorResponse(BaseModel):
    code: AppErrorCode
    message: str
    details: dict[str, Any] | None = None
