from agent.registry import TaskRegistry
from agent.engine_with_logging import LoggedAgentEngine
from triggers.scheduler import TaskScheduler
from tasks.test_task import TestTask

# Register tasks
registry = TaskRegistry()
registry.register(TestTask())

# Create engine
engine = LoggedAgentEngine(registry)

# Create scheduler with config
scheduler = TaskScheduler(
    engine=engine,
    config_path="config/schedules.yaml"
)

# Load and register jobs
scheduler.register_jobs()

print("Scheduler started (config-driven). Waiting for task execution...")

# Start scheduler loop
scheduler.start()
