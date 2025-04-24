from typing import List
from ..common.extra_base_model import ExtraBaseModel
from pydantic import Field


class SslDetails(ExtraBaseModel):
    valid_chains: List[str] = Field(default_factory=list, alias="validChains")
    invalid_chains: List[str] = Field(default_factory=list, alias="invalidChains")