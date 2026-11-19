"""
Core Types Module

Defines fundamental types used throughout the SDK including:
- Result: Unified return type for operations that can fail
- ErrorCode: Enumeration of possible error conditions
- EngineInstanceState: State of an engine instance
- ConfigType: Type of configuration/connection mode
"""

from enum import Enum
from typing import TypeVar, Generic, Optional, Any
from dataclasses import dataclass
import threading


T = TypeVar('T')


class ErrorCode(Enum):
    """Error codes for SDK operations."""
    SUCCESS = 0
    CONNECTION_FAILED = 1001
    INVALID_PARAMETER = 1002
    TIMEOUT = 1003
    INSTANCE_NOT_FOUND = 1004
    PERMISSION_DENIED = 1005
    NETWORK_ERROR = 1006
    UNKNOWN_ERROR = 9999


class EngineInstanceState(Enum):
    """State of an engine instance."""
    CREATED = 0      # Created, not connected
    CONNECTING = 1   # Connecting
    CONNECTED = 2    # Connected and available
    DISCONNECTED = 3 # Disconnected
    ERROR = 4        # Error state
    TERMINATED = 5   # Terminated


class ConfigType(Enum):
    """Type of configuration/connection mode."""
    K8S = 0      # Kubernetes mode
    LATACY = 1   # Legacy/Local mode
    LOCAL = 2    # Local mode
    CLIENT = 3   # Client mode (connect to existing engine instance)


class Result(Generic[T]):
    """
    Unified result type for operations that can fail.

    Usage:
        result = some_operation()
        if result.is_success():
            value = result.value()
        else:
            error = result.error_message()

    Can also be used with context manager:
        with result:
            process(result.value())
    """

    def __init__(
        self,
        value: Optional[T] = None,
        error_code: ErrorCode = ErrorCode.SUCCESS,
        error_message: str = ""
    ):
        self._value = value
        self._error_code = error_code
        self._error_message = error_message
        self._lock = threading.Lock()

    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        """Create a successful result with a value."""
        return cls(value=value, error_code=ErrorCode.SUCCESS, error_message="")

    @classmethod
    def failure(cls, error_code: ErrorCode, error_message: str = "") -> 'Result[T]':
        """Create a failed result with an error."""
        return cls(value=None, error_code=error_code, error_message=error_message)

    @classmethod
    def success_void(cls) -> 'Result[None]':
        """Create a successful result with no value."""
        return cls(value=None, error_code=ErrorCode.SUCCESS, error_message="")

    def is_success(self) -> bool:
        """Check if the operation succeeded."""
        return self._error_code == ErrorCode.SUCCESS

    def is_failure(self) -> bool:
        """Check if the operation failed."""
        return not self.is_success()

    def value(self) -> T:
        """Get the result value. Raises RuntimeError if failed."""
        if self.is_failure():
            raise RuntimeError(
                f"Cannot get value from failed result: "
                f"[{self._error_code.name}] {self._error_message}"
            )
        return self._value

    def value_or(self, default: T) -> T:
        """Get the result value or a default if failed."""
        if self.is_success():
            return self._value
        return default

    def value_or_none(self) -> Optional[T]:
        """Get the result value or None if failed."""
        return self._value if self.is_success() else None

    def error_code(self) -> ErrorCode:
        """Get the error code."""
        return self._error_code

    def error_message(self) -> str:
        """Get the error message."""
        return self._error_message

    def __bool__(self) -> bool:
        """Return True if successful."""
        return self.is_success()

    def __repr__(self) -> str:
        if self.is_success():
            return f"Result(success, value={self._value})"
        return f"Result(failure, error=[{self._error_code.name}] {self._error_message})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Result):
            return False
        return (
            self._value == other._value and
            self._error_code == other._error_code and
            self._error_message == other._error_message
        )


@dataclass
class EngineInstanceInfo:
    """Information about an engine instance."""
    id: str = ""
    name: str = ""
    state: EngineInstanceState = EngineInstanceState.CREATED
    created_time: str = ""
    owner: str = ""
    endpoint: str = ""
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LoadScenarioParams:
    """Parameters for loading a scenario."""
    scenario_id: str = ""
    scenario_data: Optional[bytes] = None
    options: dict = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class ChangeSpeedParams:
    """Parameters for changing simulation speed."""
    speed: float = 1.0
    immediate: bool = True


@dataclass
class RunScenarioParams:
    """Parameters for running a scenario."""
    start: bool = True
    start_time: int = 0


@dataclass
class PingInfo:
    """Network latency information."""
    engine_ping_ms: int = -1
    node_ping_ms: int = -1
    network_quality: int = 0


@dataclass
class PerformanceMetrics:
    """Performance metrics for an engine instance."""
    commands_sent: int = 0
    situations_received: int = 0
    average_latency_ms: float = 0.0
    packet_loss_rate: float = 0.0