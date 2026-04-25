from enum import StrEnum
from dataclasses import dataclass


class FaultException(Exception):
    """
    Custom exception to indicate that a Fault object has been raised.
    """
    def __init__(self, fault: Fault) -> None:
        self.fault = fault
        super().__init__(fault.description)


class FaultSeverity(StrEnum):
    """
    Represents the possible fault severities.
    """
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Fault:
    """
    Represents a single fault object that is logged into a JSON file
    for purely visual purposes.
    """
    component_name: str | None
    severity: FaultSeverity
    description: str
    timestamp: float
    exception_type: str | None
    traceback: str | None
