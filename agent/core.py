from abc import ABC, abstractmethod
from agent.context import TaskContext
from agent.result import TaskResult


class Task(ABC):
    """
    Base class for all tasks.
    Every task MUST inherit from this class.
    """

    name: str = "BASE_TASK"
    description: str = "Base task description"

    @abstractmethod
    def execute(self, context: TaskContext) -> TaskResult:
        """
        Execute task logic.

        Rules:
        - Must NOT raise unhandled exceptions
        - Must return TaskResult
        """
        pass
