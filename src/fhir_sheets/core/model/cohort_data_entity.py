from typing import Dict, Any, List, Optional, Tuple

class HeaderEntry:
    def __init__(self, data: Dict[str, Any]):
        self.entityName: Optional[str] = data.get('entityName')
        self.fieldName: Optional[str] = data.get('fieldName')
        self.jsonpath: Optional[str] = data.get('jsonpath')
        self.value_type: Optional[str] = data.get('valueType')
        self.valuesets: Optional[str] = data.get('valuesets')
        
    def __repr__(self) -> str:
        return (f"\nHeaderEntry(entityName='{self.entityName}', \n\tfieldName='{self.fieldName}', \n\tjsonpath='{self.jsonpath}',\n\tvalue_type='{self.value_type}', "
                f"\n\tvaluesets='{self.valuesets}')")
    
class PatientEntry:

    def __init__(self, entries:Dict[Tuple[str,str],str]):
        self.entries = entries

    def __repr__(self) -> str:
        return (f"PatientEntry(\n\t'{self.entries}')")
    
class CohortData:
    def __init__(self, headers: List[Dict[str,Any]], patients: List[Dict[Tuple[str,str],str]]):
        self.headers = [HeaderEntry(header_data) for header_data in headers]
        self.patients = [PatientEntry(patient_data) for patient_data in patients]

    def __repr__(self) -> str:
        return (f"CohortData(\n\t-----\n\theaders='{self.headers}',\n\t-----\n\tpatients='{self.patients}')")
    
    def get_num_patients(self):
        return len(self.patients)