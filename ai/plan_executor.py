from typing import Dict
from agent.engine_with_logging import LoggedAgentEngine


class PlanExecutor:
    """
    Validates and executes AI-generated plans.
    """

    def __init__(self, engine: LoggedAgentEngine):
        self.engine = engine

    def execute(self, plan: Dict):
        intent = plan.get("intent")

        if intent == "RUN_TASK":
            task_name = plan.get("task")
            return self.engine.run_task(task_name)

        return {
            "status": "ERROR",
            "message": "No executable action for this plan"
        }
