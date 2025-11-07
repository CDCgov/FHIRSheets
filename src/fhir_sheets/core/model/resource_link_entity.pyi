from .common import get_value_from_keys as get_value_from_keys
from typing import Any

class ResourceLink:
    originResource_keys: list[str]
    referencePath_keys: list[str]
    destinationResource_keys: list[str]
    originResource: str
    referencePath: str
    destinationResource: str
    def __init__(self, originResource: str, referencePath: str, destinationResource: str) -> None: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]): ...
