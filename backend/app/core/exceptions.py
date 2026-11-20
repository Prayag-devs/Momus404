"""
momus404 — app.core.exceptions
Domain-specific exceptions for clean error propagation.
"""

class MomusBaseException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.detail = detail


class SpecParseError(MomusBaseException):
    """Raised when an Excel test spec fails validation or parsing."""
    pass


class VaultError(MomusBaseException):
    """Raised on vault credential storage or retrieval failure."""
    pass


class OrchestrationError(MomusBaseException):
    """Raised when a test execution or background run fails."""
    pass


class RunNotFoundError(MomusBaseException):
    """Raised when a queried run_id does not exist."""
    pass
