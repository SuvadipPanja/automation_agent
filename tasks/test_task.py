from agent.core import Task
from agent.context import TaskContext
from agent.result import TaskResult, TaskStatus


class TestTask(Task):
    name = "TEST_TASK"
    description = "Simple test task for STEP-3 verification"

    def execute(self, context: TaskContext) -> TaskResult:
        return TaskResult(
            status=TaskStatus.SUCCESS,
            message="Test task executed successfully"
        )
