"""Data model for FHIR resource links (references).

This module defines the ResourceLink class which represents a reference
relationship between two FHIR resources.

Classes:
    ResourceLink: Represents a reference from one resource to another
"""

from typing import Any, Dict, List

from .common import get_value_from_keys


class ResourceLink:
    """Represents a reference relationship between two FHIR resources.
    
    A resource link defines a reference from an origin resource to a destination
    resource at a specific path within the origin resource's structure.
    
    Attributes:
        originResource: Entity name of the source resource making the reference
        referencePath: JSON path in the origin resource where the reference should be placed
        destinationResource: Entity name of the target resource being referenced
        
    Class Attributes:
        originResource_keys: Supported key variants for origin resource in input data
        referencePath_keys: Supported key variants for reference path in input data
        destinationResource_keys: Supported key variants for destination resource in input data
        
    Example:
        >>> link = ResourceLink(
        ...     originResource='Observation',
        ...     referencePath='subject',
        ...     destinationResource='Patient'
        ... )
        # This creates: Observation.subject.reference = "Patient/{id}"
    """
    
    originResource_keys: List[str] = ['OriginResource', 'Origin Resource', 'origin_resource']
    referencePath_keys: List[str] = ['ReferencePath', 'Reference Path', 'reference_path']
    destinationResource_keys: List[str] = ['DestinationResource', 'Destination Resource', 'destination_resource']
    
    def __init__(self, originResource: str, referencePath: str, destinationResource: str):
        """Initialize a ResourceLink with reference relationship information.
        
        Args:
            originResource: Entity name of the source resource
            referencePath: JSON path where the reference should be created
            destinationResource: Entity name of the target resource
            
        Example:
            >>> link = ResourceLink(
            ...     originResource='Observation',
            ...     referencePath='subject',
            ...     destinationResource='Patient'
            ... )
        """
        self.originResource: str = originResource
        self.referencePath: str = referencePath
        self.destinationResource: str = destinationResource
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a ResourceLink instance from a dictionary.
        
        Factory method to construct ResourceLink from raw dictionary data,
        typically loaded from the ResourceLinks sheet in Excel. Supports
        multiple key name variants for flexibility.
        
        Args:
            data: Dictionary with keys like 'OriginResource'/'Origin Resource'/'origin_resource',
                 'ReferencePath'/'Reference Path'/'reference_path', and
                 'DestinationResource'/'Destination Resource'/'destination_resource'
                 
        Returns:
            ResourceLink instance
            
        Example:
            >>> data = {
            ...     'OriginResource': 'Observation',
            ...     'ReferencePath': 'subject',
            ...     'DestinationResource': 'Patient'
            ... }
            >>> link = ResourceLink.from_dict(data)
        """
        return cls(
            get_value_from_keys(data, cls.originResource_keys, ''),
            get_value_from_keys(data, cls.referencePath_keys, ''),
            get_value_from_keys(data, cls.destinationResource_keys, '')
        )
        
    def __repr__(self) -> str:
        return (f"ResourceLink(originResource='{self.originResource}', "
                f"referencePath='{self.referencePath}', "
                f"destinationResource='{self.destinationResource}')")