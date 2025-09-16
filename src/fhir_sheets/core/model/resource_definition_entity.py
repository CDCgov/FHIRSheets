from typing import Any, Dict, List, Optional


class ResourceDefinition:
    """
    A class to represent a Resource Definition for FHIR initialization.
    """
    def __init__(self, entity_data: Dict[str, Any]):
        """
        Initializes the ResourceLink object from a dictionary.

        Args:
            data: A dictionary containing 'Entity name', 'ResourceType', and 'Profile(s)'.
        """
        self.entity_name = entity_data.get('Entity Name')
        self.resource_type = entity_data.get('ResourceType')
        self.profiles = entity_data.get('Profile(s)')

    def __repr__(self) -> str:
        return f"FhirEntity(entity_name='{self.entity_name}', resource_type='{self.resource_type}', profiles={self.profiles})"