from typing import Any, Dict


class TaskContext:
    """
    Shared context object passed to all tasks.
    Used for configuration, shared state, and future AI memory.
    """

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in context.
        """
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from context.
        """
        return self._data.get(key, default)

    def all(self) -> Dict[str, Any]:
        """
        Return full context data.
        """
        return dict(self._data)
