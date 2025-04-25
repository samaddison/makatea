from typing import Optional, TypeVar, Generic

from ..common.extra_base_model import ExtraBaseModel

T = TypeVar("T")


class Component(ExtraBaseModel, Generic[T]):
    status: str
    details: Optional[T] = None
