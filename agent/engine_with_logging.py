from agent.engine import AgentEngine
from agent.logger import get_agent_logger
from agent.result import TaskStatus


class LoggedAgentEngine(AgentEngine):
    """
    Agent engine with detailed execution logging.
    """

    def __init__(self, registry, context=None):
        super().__init__(registry, context)
        self.logger = get_agent_logger()

    def run_task(self, task_name: str):
        self.logger.info(f"Task '{task_name}' started")

        result = super().run_task(task_name)

        if result.status == TaskStatus.SUCCESS:
            self.logger.info(
                f"Task '{task_name}' SUCCESS | {result.message}"
            )
        else:
            self.logger.error(
                f"Task '{task_name}' FAILED | {result.message} | Error: {result.error}"
            )

        return result
