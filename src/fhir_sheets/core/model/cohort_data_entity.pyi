from .common import get_value_from_keys as get_value_from_keys
from typing import Any

class HeaderEntry:
    entityName: str | None
    fieldName: str | None
    jsonPath: str | None
    valueType: str | None
    valueSets: str | None
    def __init__(self, entityName, fieldName, jsonPath, valueType, valueSets) -> None: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]): ...

class PatientEntry:
    entries: dict[tuple[str, str], str]
    def __init__(self, entries: dict[tuple[str, str], str]) -> None: ...
    @classmethod
    def from_dict(cls, entries: dict[tuple[str, str], str]): ...

class CohortData:
    headers: list[HeaderEntry]
    patients: list[PatientEntry]
    def __init__(self, headers: list[HeaderEntry], patients: list[PatientEntry]) -> None: ...
    @classmethod
    def from_dict(cls, headers: list[dict[str, Any]], patients: list[dict[tuple[str, str], str]]): ...
    def get_num_patients(self): ...
