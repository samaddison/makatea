from pydantic import BaseModel, ConfigDict
from typing import List


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")
