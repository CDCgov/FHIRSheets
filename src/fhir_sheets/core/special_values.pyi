import abc
from . import conversion as conversion
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class AbstractStructureHandler(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

def utilFindExtensionWithURL(extension_block, url): ...
def findComponentWithCoding(components, code): ...

class PatientRaceExtensionValueHandler(AbstractStructureHandler):
    omb_categories: Incomplete
    initial_race_json: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class PatientEthnicityExtensionValueHandler(AbstractStructureHandler):
    omb_categories: Incomplete
    initial_ethnicity_json: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class PatientBirthSexExtensionValueHandler(AbstractStructureHandler):
    birth_sex_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PatientMRNIdentifierValueHandler(AbstractStructureHandler):
    patient_mrn_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PatientSSNIdentifierValueHandler(AbstractStructureHandler):
    patient_mrn_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class OrganizationIdentiferNPIValueHandler(AbstractStructureHandler):
    npi_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class OrganizationIdentiferCLIAValueHandler(AbstractStructureHandler):
    clia_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PractitionerIdentiferNPIValueHandler(AbstractStructureHandler):
    npi_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class ObservationComponentHandler(AbstractStructureHandler):
    pulse_oximetry_oxygen_flow_rate: Incomplete
    pulse_oximetry_oxygen_concentration: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class AbstractValueHandler(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def assign_value(self, final_struct, key, value, valueType): ...

class DataAbsentReasonHandler(AbstractValueHandler):
    data_absent_reason_block: Incomplete
    data_absent_reason_values: Incomplete
    def assign_value(self, final_struct, key, value, valueType) -> None: ...

custom_structure_handlers: Incomplete
custom_value_handlers: Incomplete
