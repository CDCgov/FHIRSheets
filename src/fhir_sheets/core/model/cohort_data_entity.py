"""Data models for cohort data representation.

This module defines the data structures for representing cohort data including
headers (field definitions) and patient entries (actual data values).

Classes:
    HeaderEntry: Represents a field definition with entity name, JSON path, and value type
    PatientEntry: Represents a single patient's data as key-value pairs
    CohortData: Container for headers and patient entries
"""

from typing import Dict, Any, List, Optional, Tuple

from .common import get_value_from_keys


class HeaderEntry:
    """Represents a field definition in the cohort data.
    
    A header entry defines a single field that will be populated in FHIR resources,
    including its entity name, JSON path location, data type, and optional value set.
    
    Attributes:
        entityName: Name of the entity this field belongs to (e.g., 'Patient')
        fieldName: Unique name for this field within the entity
        jsonPath: JSON path where this field's value should be placed
        valueType: FHIR data type (e.g., 'string', 'CodeableConcept', 'date')
        valueSets: Optional FHIR value set URL for validation/reference
        
    Example:
        >>> header = HeaderEntry(
        ...     entityName='Patient',
        ...     fieldName='familyName',
        ...     jsonPath='Patient.name.family',
        ...     valueType='string',
        ...     valueSets=None
        ... )
    """
    
    def __init__(self, entityName, fieldName, jsonPath, valueType, valueSets):
        """Initialize a HeaderEntry with field definition information.
        
        Args:
            entityName: Name of the entity this field belongs to
            fieldName: Unique name for this field
            jsonPath: JSON path for value placement
            valueType: FHIR data type
            valueSets: Optional value set URL
        """
        self.entityName: Optional[str] = entityName
        self.fieldName: Optional[str] = fieldName
        self.jsonPath: Optional[str] = jsonPath
        self.valueType: Optional[str] = valueType
        self.valueSets: Optional[str] = valueSets
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a HeaderEntry instance from a dictionary.
        
        Factory method to construct HeaderEntry from raw dictionary data,
        typically loaded from Excel sheets. Supports multiple key name variants.
        
        Args:
            data: Dictionary with keys like 'entityName'/'entity_name', 
                  'fieldName'/'field_name', etc.
                  
        Returns:
            HeaderEntry instance
            
        Example:
            >>> data = {
            ...     'entityName': 'Patient',
            ...     'fieldName': 'familyName',
            ...     'jsonPath': 'Patient.name.family',
            ...     'valueType': 'string'
            ... }
            >>> header = HeaderEntry.from_dict(data)
        """
        return cls(
            get_value_from_keys(data, ['entityName', 'entity_name'], ''),
            get_value_from_keys(data, ['fieldName', 'field_name'], ''),
            get_value_from_keys(data, ['jsonPath', 'json_path'], ''),
            get_value_from_keys(data, ['valueType', "value_type"], ''),
            get_value_from_keys(data, ['valueSets', 'value_sets'], '')
        )
        
    def __repr__(self) -> str:
        return (f"\nHeaderEntry(entityName='{self.entityName}', \n\tfieldName='{self.fieldName}', \n\tjsonPath='{self.jsonPath}',\n\tvalueType='{self.valueType}', "
                f"\n\tvalueSets='{self.valueSets}')")


class PatientEntry:
    """Represents a single patient's data values.
    
    A patient entry contains all field values for one patient, keyed by
    (entityName, fieldName) tuples to ensure uniqueness across entities.
    
    The original implementation restricted entry values to str which prevented
    non-string values (e.g., booleans for deceasedBoolean) from being used.
    The conversion logic can handle any JSON-serializable type, so we use Any.
    
    Attributes:
        entries: Dictionary mapping (entityName, fieldName) tuples to values
        
    Example:
        >>> patient = PatientEntry({
        ...     ('Patient', 'familyName'): 'Smith',
        ...     ('Patient', 'givenName'): 'John',
        ...     ('Observation', 'value'): '120'
        ... })
    """

    def __init__(self, entries: Dict[Tuple[str, str], Any]):
        """Initialize a PatientEntry with field values.
        
        Args:
            entries: Dictionary mapping (entityName, fieldName) tuples to values.
                    Values can be any JSON-serializable type (str, int, bool, etc.)
        """
        # Store the raw mapping; conversion functions will interpret the values
        # based on the associated valueType from the header.
        self.entries: Dict[Tuple[str, str], Any] = entries

    @classmethod
    def from_dict(cls, entries: Dict[Tuple[str, str], Any]):
        """Create a PatientEntry instance from a dictionary.
        
        Factory method to construct PatientEntry from raw dictionary data.
        
        Args:
            entries: Dictionary with (entityName, fieldName) tuple keys
                    mapping to values
                    
        Returns:
            PatientEntry instance
            
        Example:
            >>> entries = {('Patient', 'name'): 'Smith'}
            >>> patient = PatientEntry.from_dict(entries)
        """
        return cls(entries)

    def __repr__(self) -> str:
        return (f"PatientEntry(\n\t'{self.entries}')")


class CohortData:
    """Container for cohort data including headers and patient entries.
    
    This is the main data structure representing a complete cohort dataset
    with field definitions (headers) and patient data (patients).
    
    Attributes:
        headers: List of HeaderEntry objects defining all fields
        patients: List of PatientEntry objects containing patient data
        
    Methods:
        get_num_patients: Returns the number of patients in the cohort
        from_dict: Class method to create CohortData from dictionaries
        
    Example:
        >>> cohort = CohortData(
        ...     headers=[header1, header2],
        ...     patients=[patient1, patient2]
        ... )
        >>> print(cohort.get_num_patients())
        2
    """
    
    def __init__(self, headers: List[HeaderEntry], patients: List[PatientEntry]):
        """Initialize CohortData with headers and patient entries.
        
        Args:
            headers: List of HeaderEntry objects defining fields
            patients: List of PatientEntry objects with patient data
        """
        self.headers: List[HeaderEntry] = headers
        self.patients: List[PatientEntry] = patients
        
    @classmethod
    def from_dict(cls, headers: List[Dict[str, Any]], patients: List[Dict[Tuple[str, str], str]]):
        """Create a CohortData instance from dictionaries.
        
        Factory method to construct CohortData from raw dictionary data,
        typically loaded from Excel sheets.
        
        Args:
            headers: List of header dictionaries with keys: entityName, fieldName,
                    jsonPath, valueType, valueSets
            patients: List of patient dictionaries with (entityName, fieldName)
                     tuple keys mapping to values
                     
        Returns:
            CohortData instance with parsed HeaderEntry and PatientEntry objects
            
        Example:
            >>> headers = [{'entityName': 'Patient', 'fieldName': 'name', ...}]
            >>> patients = [{('Patient', 'name'): 'Smith'}]
            >>> cohort = CohortData.from_dict(headers, patients)
        """
        return cls(
            [HeaderEntry.from_dict(header) for header in headers],
            [PatientEntry.from_dict(patient) for patient in patients]
        )

    def __repr__(self) -> str:
        return (f"CohortData(\n\t-----\n\theaders='{self.headers}',\n\t-----\n\tpatients='{self.patients}')")
    
    def get_num_patients(self):
        """Get the number of patients in the cohort.
        
        Returns:
            Integer count of patients
            
        Example:
            >>> cohort.get_num_patients()
            10
        """
        return len(self.patients)