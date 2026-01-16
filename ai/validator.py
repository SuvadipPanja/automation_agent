from typing import Dict


class PlanValidator:
    """
    Ensures AI plan is safe and valid before execution.
    """

    ALLOWED_INTENTS = {"RUN_TASK", "UNKNOWN"}

    def validate(self, plan: Dict) -> Dict:
        if plan.get("intent") not in self.ALLOWED_INTENTS:
            raise ValueError("Invalid intent")

        if plan["intent"] == "RUN_TASK":
            if not plan.get("task"):
                raise ValueError("Task name missing")

        return plan
