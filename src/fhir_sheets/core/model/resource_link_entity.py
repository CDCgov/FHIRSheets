from typing import Any, Dict


class ResourceLink:
    """
    A class to represent a Fhir Reference between two resources.
    """
    def __init__(self, data: Dict[str, Any]):
        """
        Initializes the ResourceLink object from a dictionary.

        Args:
            data: A dictionary containing 'OriginResource', 'ReferencePath', and 'DestinationResource'.
        """
        self.origin_resource = data.get('OriginResource')
        self.reference_path = data.get('ReferencePath')
        self.destination_resource = data.get('DestinationResource')
        
    def __repr__(self) -> str:
        return (f"ResourceLink(origin_resource='{self.origin_resource}', "
                f"reference_path='{self.reference_path}', "
                f"destination_resource='{self.destination_resource}')")