import pprint
from typing import Dict, Any, List, Optional

class FieldEntry:
    def __init__(self, data: Dict[str, Any]):
        self.jsonpath: Optional[str] = data.get('jsonpath')
        self.value_type: Optional[str] = data.get('valueType')
        self.valuesets: Optional[str] = data.get('valuesets')
        self.values: Optional[List[str]] = data.get('values')
        
    def __repr__(self) -> str:
        return (f"FieldEntry(\n\tjsonpath='{self.jsonpath}',\n\tvalue_type='{self.value_type}', "
                f"\n\tvaluesets='{self.valuesets}', \n\tvalues={self.values})")

class EntityData:
    def __init__(self, data: Dict[str, Dict[str, Any]]):
        """
        Initializes the EntityData object. Accepts either a dictionary of raw data
        or a list of FieldEntry objects.

        Args:
            data (Dict[str, Dict[str, Any]]): A dictionary mapping names to raw field data.
            entries (List[FieldEntry]): A list of pre-created FieldEntry objects.
        """
        self.fields: Dict[str, FieldEntry] = {}
        for name, field_data in data.items():
            self.fields[name] = FieldEntry(field_data)

    def __repr__(self) -> str:
        return f"EntityData(fields=\n{pprint.pformat(self.fields, indent=4)})"
    
    def insert(self, name: str, entry: FieldEntry):
        """
        Inserts a new FieldEntry into the collection.
        
        Args:
            name (str): The referential name for the field.
            entry (FieldEntry): The FieldEntry object to insert.
        """
        self.fields[name] = entry

    def remove(self, name: str) -> bool:
        """
        Removes a FieldEntry by its referential name.
        
        Args:
            name (str): The referential name of the field to remove.
        
        Returns:
            bool: True if the field was removed, False otherwise.
        """
        if name in self.fields:
            del self.fields[name]
            return True
        return False
    
class CohortData:
    def __init__(self, data: Dict[str, EntityData] = None):
        """
        Initializes the CohortData object.

        Args:
            data (Dict[str, EntityData]): A dictionary where keys are entity names
                                          and values are EntityData objects.
        """
        self.entities: Dict[str, EntityData] = {}
        self.num_entries = 0
        if data:
            self.entities.update(data)
            
    def __repr__(self) -> str:
        return f"CohortData(entities={self.entities})"
    
    def insert_entity(self, name: str, entity_data: EntityData):
        """
        Inserts a new EntityData object into the cohort.

        Args:
            name (str): The name of the entity (e.g., 'PrimaryPatient').
            entity_data (EntityData): The EntityData object to insert.
        """
        self.entities[name] = entity_data
        
    def remove_entity(self, name: str) -> bool:
        """
        Removes an EntityData object by its name.

        Args:
            name (str): The name of the entity to remove.

        Returns:
            bool: True if the entity was removed, False otherwise.
        """
        if name in self.entities:
            del self.entities[name]
            return True
        return False