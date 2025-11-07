from .common import get_value_from_keys as get_value_from_keys
from typing import Any

class ResourceDefinition:
    entityName_keys: list[str]
    resourceType_keys: list[str]
    profile_keys: list[str]
    entityName: str
    resourceType: str
    profiles: list[str]
    def __init__(self, entityName: str, resourceType: str, profiles: list[str]) -> None: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]): ...
