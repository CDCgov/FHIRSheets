from typing import Any, Dict, List, Optional

from .common import get_value_from_keys


class ResourceDefinition:
    """
    A class to represent a Resource Definition for FHIR initialization.
    """
    entityName_keys = ['Entity Name', 'name', 'entity_name']
    resourceType_keys = ['ResourceType', 'resource_type', 'type']
    profile_keys = ['Profile(s)', 'profiles', 'profile_list']
    
    def __init__(self, entityName: str, resourceType: str, profiles: List[str]):
        """
        Initializes the ResourceLink object from a dictionary.

        Args:
            data: A dictionary containing 'EntityName', 'ResourceType', and 'Profile(s)'.
        """
        self.entityName = entityName
        self.resourceType = resourceType
        self.profiles = profiles
        
    @classmethod
    def from_dict(cls, data:  Dict[str, Any]):
        return cls(get_value_from_keys(data, cls.entityName_keys, ''), get_value_from_keys(data, cls.resourceType_keys, ''), get_value_from_keys(data, cls.profile_keys, []))

    def __repr__(self) -> str:
        return f"ResourceDefinition(entityName='{self.entityName}', resourceType='{self.resourceType}', profiles={self.profiles})"