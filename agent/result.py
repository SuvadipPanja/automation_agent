from enum import Enum
from typing import Any, Optional
from datetime import datetime


class TaskStatus(Enum):
    """
    Fixed execution states for every task.
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TaskResult:
    """
    Standard result object returned by every task.
    """

    def __init__(
        self,
        status: TaskStatus,
        message: str,
        data: Optional[Any] = None,
        error: Optional[str] = None
    ):
        self.status = status
        self.message = message
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()

    def is_success(self) -> bool:
        """
        Check if task completed successfully.
        """
        return self.status == TaskStatus.SUCCESS

    def to_dict(self) -> dict:
        """
        Convert result to dictionary (API / log / DB ready).
        """
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }
