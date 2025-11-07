from typing import Dict, Any, List, Optional, Tuple

from .common import get_value_from_keys

class HeaderEntry:
    def __init__(self, entityName, fieldName, jsonPath, valueType, valueSets):
        self.entityName: Optional[str] = entityName
        self.fieldName: Optional[str] = fieldName
        self.jsonPath: Optional[str] = jsonPath
        self.valueType: Optional[str] = valueType
        self.valueSets: Optional[str] = valueSets
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(get_value_from_keys(data, ['entityName', 'entity_name'], ''), get_value_from_keys(data, ['fieldName', 'field_name'], ''),get_value_from_keys(data, ['jsonPath', 'json_path'], ''),get_value_from_keys(data, ['valueType', "value_type"], ''),get_value_from_keys(data, ['valueSets', 'value_sets'], ''))
        
    def __repr__(self) -> str:
        return (f"\nHeaderEntry(entityName='{self.entityName}', \n\tfieldName='{self.fieldName}', \n\tjsonPath='{self.jsonPath}',\n\tvalueType='{self.valueType}', "
                f"\n\tvalueSets='{self.valueSets}')")
    
class PatientEntry:
    def __init__(self, entries:Dict[Tuple[str,str],str]):
        self.entries:Dict[Tuple[str,str],str] = entries
       
    @classmethod 
    def from_dict(cls, entries:Dict[Tuple[str,str],str]):
        return cls(entries)

    def __repr__(self) -> str:
        return (f"PatientEntry(\n\t'{self.entries}')")
    
class CohortData:
    def __init__(self, headers: List[HeaderEntry], patients: List[PatientEntry]):
        self.headers:List[HeaderEntry] = headers
        self.patients:List[PatientEntry] = patients
        
    @classmethod
    def from_dict(cls, headers: List[Dict[str, Any]], patients: List[Dict[Tuple[str,str],str]]):
        return cls([HeaderEntry.from_dict(header) for header in headers], [PatientEntry.from_dict(patient) for patient in patients])

    def __repr__(self) -> str:
        return (f"CohortData(\n\t-----\n\theaders='{self.headers}',\n\t-----\n\tpatients='{self.patients}')")
    
    def get_num_patients(self):
        return len(self.patients)