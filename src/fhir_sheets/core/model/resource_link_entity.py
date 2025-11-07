from typing import Any, Dict, List

from .common import get_value_from_keys


class ResourceLink:
    """
    A class to represent a Fhir Reference between two resources.
    """
    originResource_keys: List[str] = ['OriginResource', 'Origin Resource', 'origin_resource']
    referencePath_keys: List[str] = ['ReferencePath', 'Reference Path', 'reference_path']
    destinationResource_keys: List[str] = ['DestinationResource', 'Destination Resource', 'destination_resource']
    def __init__(self, originResource: str, referencePath: str, destinationResource: str):
        """
        Initializes the ResourceLink object from a dictionary.

        Args:
            data: A dictionary containing 'OriginResource', 'ReferencePath', and 'DestinationResource'.
        """
        self.originResource: str = originResource
        self.referencePath: str = referencePath
        self.destinationResource: str = destinationResource
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(get_value_from_keys(data, cls.originResource_keys, ''), get_value_from_keys(data, cls.referencePath_keys, ''), 
            get_value_from_keys(data, cls.destinationResource_keys, ''))
        
    def __repr__(self) -> str:
        return (f"ResourceLink(originResource='{self.originResource}', "
                f"referencePath='{self.referencePath}', "
                f"destinationResource='{self.destinationResource}')")