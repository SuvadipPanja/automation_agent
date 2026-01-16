from typing import Dict
from agent.core import Task


class TaskRegistry:
    """
    Registry to manage all available tasks.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def register(self, task: Task) -> None:
        """
        Register a new task.
        """
        if task.name in self._tasks:
            raise ValueError(f"Task '{task.name}' is already registered")
        self._tasks[task.name] = task

    def get(self, name: str) -> Task:
        """
        Get a task by name.
        """
        if name not in self._tasks:
            raise KeyError(f"Task '{name}' not found")
        return self._tasks[name]

    def all_tasks(self) -> Dict[str, Task]:
        """
        Return all registered tasks.
        """
        return dict(self._tasks)
