import schedule
import yaml
from pathlib import Path
from typing import Dict, List

from triggers.scheduler import TaskScheduler
from agent.engine_with_logging import LoggedAgentEngine


class SchedulerManager:
    """
    Manages scheduler lifecycle and allows reload from config.
    """

    def __init__(self, engine: LoggedAgentEngine, config_path: str):
        self.engine = engine
        self.config_path = Path(config_path)
        self.scheduler = TaskScheduler(engine, config_path)

    def load_config(self) -> Dict:
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def list_schedules(self) -> List[Dict]:
        config = self.load_config()
        return config.get("schedules", [])

    def reload(self) -> None:
        """
        Clear all existing jobs and reload from config.
        """
        schedule.clear()
        self.scheduler.register_jobs()
