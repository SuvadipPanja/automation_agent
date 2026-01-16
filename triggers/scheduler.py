import time
import schedule
import yaml
from pathlib import Path
from typing import Dict, List

from agent.engine_with_logging import LoggedAgentEngine
from agent.result import TaskResult


class TaskScheduler:
    """
    Config-driven, continuous task scheduler.
    """

    def __init__(self, engine: LoggedAgentEngine, config_path: str):
        self.engine = engine
        self.config_path = Path(config_path)
        self.jobs: List[Dict] = []

    def load_config(self) -> Dict:
        """
        Load scheduler configuration from YAML file.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Schedule config not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def register_jobs(self) -> None:
        """
        Register jobs from config file.
        """
        config = self.load_config()
        schedules = config.get("schedules", [])

        for entry in schedules:
            if not entry.get("enabled", False):
                continue

            task_name = entry["task"]
            time_str = entry["time"]
            job_type = entry.get("type", "daily")

            if job_type == "daily":
                self._register_daily(task_name, time_str)

    def _register_daily(self, task_name: str, time_str: str) -> None:
        """
        Register daily task.
        """

        def job():
            result: TaskResult = self.engine.run_task(task_name)
            return result

        schedule.every().day.at(time_str).do(job)

        self.jobs.append({
            "task": task_name,
            "time": time_str,
            "type": "daily"
        })

    def start(self) -> None:
        """
        Start scheduler loop (blocking).
        """
        while True:
            schedule.run_pending()
            time.sleep(1)
