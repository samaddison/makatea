from pydantic import BaseModel, ConfigDict


class ExtraBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")
