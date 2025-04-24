from datetime import datetime
from typing import List, Optional
from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class Runnable(ExtraBaseModel):
    target: str


class Execution(ExtraBaseModel):
    time: datetime
    status: Optional[str] = None


class CronTask(ExtraBaseModel):
    runnable: Runnable
    expression: str
    last_execution: Optional[Execution] = Field(None, alias="lastExecution")
    next_execution: Optional[Execution] = Field(None, alias="nextExecution")


class FixedDelayTask(ExtraBaseModel):
    runnable: Runnable
    initial_delay: int = Field(alias="initialDelay")
    interval: int
    last_execution: Optional[Execution] = Field(None, alias="lastExecution")
    next_execution: Optional[Execution] = Field(None, alias="nextExecution")


class FixedRateTask(ExtraBaseModel):
    runnable: Runnable
    initial_delay: int = Field(alias="initialDelay")
    interval: int
    last_execution: Optional[Execution] = Field(None, alias="lastExecution")
    next_execution: Optional[Execution] = Field(None, alias="nextExecution")


class CustomTask(ExtraBaseModel):
    pass


class ScheduledTasks(ExtraBaseModel):
    cron: List[CronTask] = []
    fixed_delay: List[FixedDelayTask] = Field([], alias="fixedDelay")
    fixed_rate: List[FixedRateTask] = Field([], alias="fixedRate")
    custom: List[CustomTask] = []