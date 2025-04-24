import pytest
from datetime import datetime

from src.actuator.containers.scheduledtasks.models import (
    ScheduledTasks,
    CronTask,
    FixedRateTask,
    FixedDelayTask,
    Runnable,
    Execution,
)


def test_scheduled_tasks_model_parsing():
    # Test JSON data
    json_data = {
        "cron": [
            {
                "runnable": {
                    "target": "com.example.TaskClass.cronTask"
                },
                "expression": "*/10 * * * * *",
                "lastExecution": {
                    "time": "2025-04-23T10:59:50.001274700Z",
                    "status": "SUCCESS"
                },
                "nextExecution": {
                    "time": "2025-04-23T10:59:59.999767Z"
                }
            }
        ],
        "fixedDelay": [],
        "fixedRate": [
            {
                "runnable": {
                    "target": "com.example.TaskClass.fixedRateTask"
                },
                "initialDelay": 0,
                "interval": 10000,
                "lastExecution": {
                    "time": "2025-04-23T10:59:45.559378500Z",
                    "status": "SUCCESS"
                },
                "nextExecution": {
                    "time": "2025-04-23T10:59:55.550767Z"
                }
            }
        ],
        "custom": []
    }

    # Parse the JSON
    tasks = ScheduledTasks.model_validate(json_data)

    # Test cron tasks
    assert len(tasks.cron) == 1
    assert tasks.cron[0].runnable.target == "com.example.TaskClass.cronTask"
    assert tasks.cron[0].expression == "*/10 * * * * *"
    assert tasks.cron[0].last_execution is not None
    assert tasks.cron[0].last_execution.status == "SUCCESS"
    assert isinstance(tasks.cron[0].last_execution.time, datetime)
    assert tasks.cron[0].next_execution is not None
    assert isinstance(tasks.cron[0].next_execution.time, datetime)

    # Test fixed rate tasks
    assert len(tasks.fixed_rate) == 1
    assert tasks.fixed_rate[0].runnable.target == "com.example.TaskClass.fixedRateTask"
    assert tasks.fixed_rate[0].initial_delay == 0
    assert tasks.fixed_rate[0].interval == 10000
    assert tasks.fixed_rate[0].last_execution is not None
    assert tasks.fixed_rate[0].last_execution.status == "SUCCESS"
    assert isinstance(tasks.fixed_rate[0].last_execution.time, datetime)
    assert tasks.fixed_rate[0].next_execution is not None
    assert isinstance(tasks.fixed_rate[0].next_execution.time, datetime)

    # Test empty lists
    assert len(tasks.fixed_delay) == 0
    assert len(tasks.custom) == 0