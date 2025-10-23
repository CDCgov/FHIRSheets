import abc
from . import conversion as conversion
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class AbstractCustomValueHandler(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class PatientRaceExtensionValueHandler(AbstractCustomValueHandler):
    omb_categories: Incomplete
    initial_race_json: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class PatientEthnicityExtensionValueHandler(AbstractCustomValueHandler):
    omb_categories: Incomplete
    initial_ethnicity_json: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

class PatientBirthSexExtensionValueHandler(AbstractCustomValueHandler):
    birth_sex_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PatientMRNIdentifierValueHandler(AbstractCustomValueHandler):
    patient_mrn_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PatientSSNIdentifierValueHandler(AbstractCustomValueHandler):
    patient_mrn_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class OrganizationIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class OrganizationIdentiferCLIAValueHandler(AbstractCustomValueHandler):
    clia_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class PractitionerIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value) -> None: ...

class ObservationComponentHandler(AbstractCustomValueHandler):
    pulse_oximetry_oxygen_flow_rate: Incomplete
    pulse_oximetry_oxygen_concentration: Incomplete
    def assign_value(self, json_path, resource_definition, dataType, final_struct, key, value): ...

def utilFindExtensionWithURL(extension_block, url): ...
def findComponentWithCoding(components, code): ...

custom_handlers: Incomplete
