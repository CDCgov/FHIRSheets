"""Data model for FHIR resource definitions.

This module defines the ResourceDefinition class which represents the metadata
for a FHIR resource entity including its name, type, and profiles.

Classes:
    ResourceDefinition: Represents a FHIR resource entity definition
"""

from typing import Any, Dict, List, Optional

from .common import get_value_from_keys


class ResourceDefinition:
    """Represents a FHIR resource entity definition.
    
    A resource definition specifies the metadata for a FHIR resource entity,
    including its unique entity name, FHIR resource type, and optional profiles.
    
    Attributes:
        entityName: Unique identifier for this entity (e.g., 'Patient', 'PrimaryCareObservation')
        resourceType: FHIR resource type (e.g., 'Patient', 'Observation', 'Condition')
        profiles: List of FHIR profile URLs this resource conforms to
        
    Class Attributes:
        entityName_keys: Supported key variants for entity name in input data
        resourceType_keys: Supported key variants for resource type in input data
        profile_keys: Supported key variants for profiles in input data
        
    Example:
        >>> definition = ResourceDefinition(
        ...     entityName='USCorePatient',
        ...     resourceType='Patient',
        ...     profiles=['http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient']
        ... )
    """
    
    entityName_keys: List[str] = ['Entity Name', 'name', 'entity_name']
    resourceType_keys: List[str] = ['ResourceType', 'resource_type', 'type']
    profile_keys: List[str] = ['Profile(s)', 'profiles', 'profile_list']
    
    def __init__(self, entityName: str, resourceType: str, profiles: List[str]):
        """Initialize a ResourceDefinition with entity metadata.
        
        Args:
            entityName: Unique identifier for this entity
            resourceType: FHIR resource type
            profiles: List of FHIR profile URLs (can be empty list)
            
        Example:
            >>> definition = ResourceDefinition(
            ...     entityName='Patient',
            ...     resourceType='Patient',
            ...     profiles=[]
            ... )
        """
        self.entityName: str = entityName
        self.resourceType: str = resourceType
        self.profiles: List[str] = profiles
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a ResourceDefinition instance from a dictionary.
        
        Factory method to construct ResourceDefinition from raw dictionary data,
        typically loaded from the ResourceDefinitions sheet in Excel. Supports
        multiple key name variants for flexibility.
        
        Args:
            data: Dictionary with keys like 'Entity Name'/'name'/'entity_name',
                 'ResourceType'/'resource_type'/'type', and optionally
                 'Profile(s)'/'profiles'/'profile_list' (list of profile URLs)
                 
        Returns:
            ResourceDefinition instance
            
        Example:
            >>> data = {
            ...     'Entity Name': 'Patient',
            ...     'ResourceType': 'Patient',
            ...     'Profile(s)': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient']
            ... }
            >>> definition = ResourceDefinition.from_dict(data)
        """
        return cls(
            get_value_from_keys(data, cls.entityName_keys, ''),
            get_value_from_keys(data, cls.resourceType_keys, ''),
            get_value_from_keys(data, cls.profile_keys, [])
        )

    def __repr__(self) -> str:
        return f"ResourceDefinition(entityName='{self.entityName}', resourceType='{self.resourceType}', profiles={self.profiles})"