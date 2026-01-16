from typing import Optional
from agent.registry import TaskRegistry
from agent.context import TaskContext
from agent.result import TaskResult, TaskStatus


class AgentEngine:
    """
    Core execution engine of the automation agent.
    Responsible for running tasks safely and consistently.
    """

    def __init__(self, registry: TaskRegistry, context: Optional[TaskContext] = None):
        self.registry = registry
        self.context = context or TaskContext()

    def run_task(self, task_name: str) -> TaskResult:
        """
        Execute a task by name.
        """
        try:
            task = self.registry.get(task_name)

            # Mark task as running
            result = task.execute(self.context)

            if not isinstance(result, TaskResult):
                return TaskResult(
                    status=TaskStatus.FAILED,
                    message=f"Task '{task_name}' did not return TaskResult",
                    error="Invalid return type"
                )

            return result

        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                message=f"Task '{task_name}' crashed during execution",
                error=str(e)
            )
