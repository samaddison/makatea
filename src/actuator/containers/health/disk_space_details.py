from ..common.extra_base_model import ExtraBaseModel


class DiskSpaceDetails(ExtraBaseModel):
    total: int
    free: int
    threshold: int
    path: str
    exists: bool