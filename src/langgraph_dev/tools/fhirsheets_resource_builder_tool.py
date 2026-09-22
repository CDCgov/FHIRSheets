"""
FHIRSheets Resource Builder Toolkit for LangGraph Agent

This module provides high-level tools for creating complete FHIR resources
by orchestrating calls to the FHIRSheetsXlsxToolkit.
"""

import json
from typing import List, Literal, Optional, Type

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import BaseModel, Field

from .fhirsheets_xlsx_tool import FhirSheetsXlsxToolkit


# FHIR Data Type Models
class CodeableConcept(BaseModel):
    """Represents a FHIR CodeableConcept data type."""
    system: Optional[str] = Field(default=None, description="The code system (e.g., http://snomed.info/sct, http://loinc.org)")
    code: str = Field(..., description="The code value")
    display: Optional[str] = Field(default=None, description="Human-readable representation of the code")
    
    def sheet_string(self) -> str:
        """
        Convert CodeableConcept to FHIRSheets string format using caret (^) as delimiter.
        Format: system^code^display or code^display or just code
        Matches HL7 VS format.
        """
        parts = [self.code]
        if self.system:
            parts.insert(0, self.system)
        if self.display:
            parts.append(self.display)
        return "^".join(parts)


class Quantity(BaseModel):
    """Represents a FHIR Quantity data type."""
    value: Optional[float] = Field(default=None, description="The numerical value")
    unit: Optional[str] = Field(default=None, description="The unit of measure (e.g., mg, kg, %)")
    
    def sheet_string(self) -> str:
        """
        Convert Quantity to FHIRSheets string format using caret (^) as delimiter.
        Format: value^unit (always includes delimiter even if values are missing)
        """
        value_str = str(self.value) if self.value is not None else ""
        unit_str = self.unit if self.unit else ""
        return f"{value_str}^{unit_str}"


# Pydantic Input Models

class ResourceBuilderInputBase(BaseModel):
    """Base class for all resource builder input models."""
    entity_name: str = Field(..., description="The entity name for this resource")
    row_index: int = Field(..., description="The 0-based patient row index")
    xlsx_path: Optional[str] = Field(default=None, description="Path to Excel file")


class CreatePatientInput(ResourceBuilderInputBase):
    """Input for creating a Patient resource."""
    given_name: Optional[str] = Field(default=None, description="Patient's given (first) name")
    family_name: Optional[str] = Field(default=None, description="Patient's family (last) name")
    birth_date: Optional[str] = Field(default=None, description="Patient's birth date (YYYY-MM-DD)")
    name_use: Optional[Literal["usual", "official", "temp", "nickname", "anonymous", "old", "maiden"]] = Field(default='official', description="Use of the name (usual, official, temp, nickname, anonymous, old, maiden)")
    gender: Optional[str] = Field(default=None, description="Patient's gender (male, female, other, unknown)")
    address: Optional[str] = Field(default=None, description="Patient's address")
    mrn: Optional[str] = Field(default=None, description="Medical Record Number")
    ssn: Optional[str] = Field(default=None, description="Social Security Number")
    telecom: Optional[str] = Field(default=None, description="Patient's phone number")
    race: Optional[Literal["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander"]] = Field(default=None, description="Patient's race (White, Black or African American, Asian, American Indian or Alaska Native, Native Hawaiian or Other Pacific Islander)")
    ethnicity: Optional[Literal["Hispanic or Latino", "Not Hispanic or Latino"]] = Field(default=None, description="Patient's ethnicity (Hispanic or Latino, Not Hispanic or Latino)")
    language: Optional[CodeableConcept] = Field(default=None, description="Patient's preferred language as a CodeableConcept (system, code, display)")


class CreatePractitionerInput(ResourceBuilderInputBase):
    """Input for creating a Practitioner resource."""
    given_name: Optional[str] = Field(default=None, description="Practitioner's given name")
    family_name: Optional[str] = Field(default=None, description="Practitioner's family name")
    provider_role: Optional[CodeableConcept] = Field(default=None, description="Provider role as a CodeableConcept (system, code, display)")
    provider_specialty: Optional[CodeableConcept] = Field(default=None, description="Provider specialty as a CodeableConcept (system, code, display)")
    phone_number: Optional[str] = Field(default=None, description="Phone number")
    phone_number_use: Optional[Literal["home", "work", "temp", "old", "mobile"]] = Field(default="work", description="Phone number use (home, work, temp, old, mobile)")
    national_provider_identifier: Optional[str] = Field(default=None, description="National Provider Identifier (NPI)")


class CreateEncounterInput(ResourceBuilderInputBase):
    """Input for creating an Encounter resource."""
    encounter_identifier_namespace: Optional[str] = Field(default=None, description="Encounter identifier namespace")
    encounter_identifier: Optional[str] = Field(default=None, description="Encounter identifier value")
    status: Optional[str] = Field(default=None, description="Encounter status")
    encounter_class: Optional[CodeableConcept] = Field(default=None, description="Encounter patient classification as CodeableConcept")
    specific_encounter_type: Optional[CodeableConcept] = Field(default=None, description="Specific encounter type as CodeableConcept")
    start_date: Optional[str] = Field(default=None, description="Encounter start date/time")
    end_date: Optional[str] = Field(default=None, description="Encounter end date/time")
    reason_encounter_took_place: Optional[CodeableConcept] = Field(default=None, description="Reason encounter took place as CodeableConcept")
    encounter_discharge_disposition: Optional[CodeableConcept] = Field(default=None, description="Encounter discharge disposition as CodeableConcept")
    encounter_note: Optional[str] = Field(default=None, description="Encounter note text")


class CreateObservationInput(ResourceBuilderInputBase):
    """Input for creating an Observation resource."""
    observation_type: str = Field(..., description="Type of observation")
    code: Optional[str] = Field(default=None, description="Observation code")
    value: Optional[str] = Field(default=None, description="Observation value")
    unit: Optional[str] = Field(default=None, description="Unit of measure")
    effective_date: Optional[str] = Field(default=None, description="Effective date/time")
    profiles: Optional[str] = Field(default=None, description="Comma-separated profile URLs")


class CreatePractitionerRoleInput(ResourceBuilderInputBase):
    """Input for creating a PractitionerRole resource."""
    code: Optional[CodeableConcept] = Field(default=None, description="Role code")
    specialty: Optional[CodeableConcept] = Field(default=None, description="Specialty code")


class CreateLocationInput(ResourceBuilderInputBase):
    """Input for creating a Location resource."""
    name: Optional[str] = Field(default=None, description="Location name")
    address: Optional[str] = Field(default=None, description="Location address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State")
    postal_code: Optional[str] = Field(default=None, description="Postal code")


class CreateOrganizationInput(ResourceBuilderInputBase):
    """Input for creating an Organization resource."""
    name: Optional[str] = Field(default=None, description="Organization name")
    npi: Optional[str] = Field(default=None, description="Organization NPI")
    address: Optional[str] = Field(default=None, description="Organization address")
    phone: Optional[str] = Field(default=None, description="Phone number")


class CreateImmunizationInput(ResourceBuilderInputBase):
    """Input for creating an Immunization resource."""
    status: Optional[str] = Field(default=None, description="Immunization current status")
    reason_code: Optional[CodeableConcept] = Field(default=None, description="Reason immunization administered as CodeableConcept")
    vaccine_code: Optional[CodeableConcept] = Field(default=None, description="Vaccine code as CodeableConcept")
    occurrence_date: Optional[str] = Field(default=None, description="Date vaccine was administered")
    primary_source: Optional[bool] = Field(default=False, description="EHR primary source of vaccine record")
    lot_number: Optional[str] = Field(default=None, description="Vaccine lot number")
    dose_quantity: Optional[Quantity] = Field(default=None, description="Vaccine dose as Quantity")


class CreateAllergyIntoleranceInput(ResourceBuilderInputBase):
    """Input for creating an AllergyIntolerance resource."""
    code: Optional[CodeableConcept] = Field(default=None, description="Allergy/intolerance code as CodeableConcept")
    clinical_status: Optional[CodeableConcept] = Field(default=None, description="Clinical status as CodeableConcept")
    verification_status: Optional[CodeableConcept] = Field(default=None, description="Verification status as CodeableConcept")
    category: Optional[str] = Field(default=None, description="Category")
    criticality: Optional[str] = Field(default=None, description="Criticality")


class CreateProcedureInput(ResourceBuilderInputBase):
    """Input for creating a Procedure resource."""
    code: Optional[CodeableConcept] = Field(default=None, description="Procedure code as CodeableConcept")
    status: Optional[str] = Field(default=None, description="Procedure status")
    performed_date: Optional[str] = Field(default=None, description="Date/time procedure was performed")


class CreateEncounterDiagnosisConditionInput(ResourceBuilderInputBase):
    """Input for creating an Encounter Diagnosis Condition resource."""
    code: Optional[CodeableConcept] = Field(default=None, description="Condition code as CodeableConcept")
    clinical_status: Optional[CodeableConcept] = Field(default=None, description="Clinical status as CodeableConcept")
    verification_status: Optional[CodeableConcept] = Field(default=None, description="Verification status as CodeableConcept")
    onset_date: Optional[str] = Field(default=None, description="Onset date")


class CreateHealthProblemConditionInput(ResourceBuilderInputBase):
    """Input for creating a Health Problem/Concern Condition resource."""
    code: Optional[CodeableConcept] = Field(default=None, description="Condition code as CodeableConcept")
    clinical_status: Optional[CodeableConcept] = Field(default=None, description="Clinical status as CodeableConcept")
    verification_status: Optional[CodeableConcept] = Field(default=None, description="Verification status as CodeableConcept")
    category_code: Literal["problem-list-item", "health-concern"] = Field(..., description="Category code: 'problem-list-item' or 'health-concern'")
    onset_date: Optional[str] = Field(default=None, description="Onset date")


class CreateMedicationRequestInput(ResourceBuilderInputBase):
    """Input for creating a MedicationRequest resource."""
    medication_code: Optional[CodeableConcept] = Field(default=None, description="Medication code (RxNorm)")
    status: Optional[str] = Field(default=None, description="Status")
    intent: Optional[str] = Field(default=None, description="Intent")
    authored_on: Optional[str] = Field(default=None, description="Date/time request was authored")
    dosage_instruction: Optional[str] = Field(default=None, description="Dosage instructions")
    medication_route: Optional[CodeableConcept] = Field(default=None, description="Medication route as CodeableConcept")
    medication_dosage: Optional[Quantity] = Field(default=None, description="Medication dosage as Quantity")


class CreateDiagnosticReportInput(ResourceBuilderInputBase):
    """Input for creating a DiagnosticReport resource."""
    status: Optional[str] = Field(default=None, description="Report status")
    code: Optional[CodeableConcept] = Field(default=None, description="Report code as CodeableConcept")
    effective_date: Optional[str] = Field(default=None, description="Effective date/time")
    issued_date: Optional[str] = Field(default=None, description="Issued date/time")


class CreateLaboratoryResultInput(ResourceBuilderInputBase):
    """Input for creating a Laboratory Result Observation resource."""
    status: Optional[str] = Field(default=None, description="Observation status")
    code: Optional[CodeableConcept] = Field(default=None, description="Lab test code (LOINC) as CodeableConcept")
    category: Optional[CodeableConcept] = Field(default=None, description="Observation category as CodeableConcept")
    record_date: Optional[str] = Field(default=None, description="Record date/time")
    value: Optional[Quantity] = Field(default=None, description="Lab result value as Quantity")


class CreateVitalSignInput(ResourceBuilderInputBase):
    """Input for creating a Vital Sign Observation resource."""
    type: Optional[CodeableConcept] = Field(default=None, description="Vital sign type as CodeableConcept")
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Vital sign value as Quantity")
    status: Optional[str] = Field(default=None, description="Vital sign status")
    category: Optional[CodeableConcept] = Field(default=None, description="Vital sign category as CodeableConcept")


class CreateHeightInput(ResourceBuilderInputBase):
    """Input for creating a Height Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Height value as Quantity")


class CreateWeightInput(ResourceBuilderInputBase):
    """Input for creating a Weight Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Weight value as Quantity")


class CreateBodyTemperatureInput(ResourceBuilderInputBase):
    """Input for creating a Body Temperature Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Body temperature value as Quantity")


class CreateRespiratoryRateInput(ResourceBuilderInputBase):
    """Input for creating a Respiratory Rate Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Respiratory rate value as Quantity")


class CreateHeartRateInput(ResourceBuilderInputBase):
    """Input for creating a Heart Rate Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Heart rate value as Quantity")


class CreateOxygenConcentrationInput(ResourceBuilderInputBase):
    """Input for creating an Oxygen Concentration Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[Quantity] = Field(default=None, description="Oxygen concentration value as Quantity")


class CreateBloodPressureInput(ResourceBuilderInputBase):
    """Input for creating a Blood Pressure Observation resource."""
    effective_datetime: Optional[str] = Field(default=None, description="Effective date/time")
    systolic_value: Optional[Quantity] = Field(default=None, description="Systolic blood pressure value as Quantity")
    diastolic_value: Optional[Quantity] = Field(default=None, description="Diastolic blood pressure value as Quantity")


class CreatePulseOximetryInput(ResourceBuilderInputBase):
    """Input for creating a Pulse Oximetry Observation resource."""
    status: Optional[str] = Field(default=None, description="Observation status")
    effective_date: Optional[str] = Field(default=None, description="Effective date/time")
    flow_rate: Optional[Quantity] = Field(default=None, description="Inhaled oxygen flow rate")
    concentration: Optional[Quantity] = Field(default=None, description="Inhaled oxygen concentration")


class CreatePediatricBmiForAgeInput(ResourceBuilderInputBase):
    """Input for creating a Pediatric BMI for Age Observation resource."""
    value: Optional[str] = Field(default=None, description="BMI value")
    effective_date: Optional[str] = Field(default=None, description="Effective date/time")


class CreateDeviceInput(ResourceBuilderInputBase):
    """Input for creating a Device resource."""
    identifier: Optional[str] = Field(default=None, description="Device identifier")
    carrier_hrf: Optional[str] = Field(default=None, description="Carrier HRF")
    manufacture_date: Optional[str] = Field(default=None, description="Manufacture date")
    expiration_date: Optional[str] = Field(default=None, description="Expiration date")
    lot_number: Optional[str] = Field(default=None, description="Lot number")
    serial_number: Optional[str] = Field(default=None, description="Serial number")
    type: Optional[CodeableConcept] = Field(default=None, description="Device type as CodeableConcept")


class CreateSmokingStatusInput(ResourceBuilderInputBase):
    """Input for creating a Smoking Status Observation resource."""
    status: Optional[str] = Field(default=None, description="Observation status")
    code: Optional[CodeableConcept] = Field(default=None, description="Smoking status code as CodeableConcept")
    category: Optional[CodeableConcept] = Field(default=None, description="Observation category as CodeableConcept")
    effective_date: Optional[str] = Field(default=None, description="Effective date/time")
    value: Optional[CodeableConcept] = Field(default=None, description="Smoking status value as CodeableConcept")


class CreateServiceRequestInput(ResourceBuilderInputBase):
    """Input for creating a ServiceRequest resource."""
    status: Optional[str] = Field(default=None, description="Service Request Status")
    intent: Optional[str] = Field(default=None, description="Service Request Intent")
    code: Optional[CodeableConcept] = Field(default=None, description="Service Request Code as CodeableConcept")
    occurrence_date_time: Optional[str] = Field(default=None, description="Service Request Occurrence Date")


# Base Tool Class with Helper Methods
class ResourceBuilderBaseTool(BaseTool):
    """Base class for resource builder tools with helper methods."""
    
    xlsx_toolkit: FhirSheetsXlsxToolkit
    
    class Config:
        arbitrary_types_allowed = True
    
    def _ensure_resource_definition(self, entity_name: str, resource_type: str, profiles: Optional[str], xlsx_path: Optional[str], value_type: Optional[str] = None) -> dict:
        """Ensure a resource definition exists and copy reference columns.
        
        Args:
            entity_name: The entity name for the resource
            resource_type: The FHIR resource type
            profiles: Optional profile URLs
            xlsx_path: Path to the Excel file
            value_type: Optional value type filter for copying reference columns
        
        Returns a composite result with keys:
        - success: Overall success status
        - check_exists: Result from check_resource_definition_exists call
        - create_definition: Result from create_resource_definition call (if needed)
        """
        tools = self.xlsx_toolkit.get_tools()
        
        # Step 1: Check if resource definition already exists
        check_exists_tool = next(t for t in tools if t.name == "check_resource_definition_exists")
        check_result_str = check_exists_tool._run(entity_name=entity_name)
        check_result = json.loads(check_result_str)
        
        # Step 2: Create resource definition only if it doesn't exist
        create_result = {"success": True, "message": "Skipped - resource definition already exists"}
        if check_result.get("success") and not check_result.get("exists"):
            create_def_tool = next(t for t in tools if t.name == "create_resource_definition")
            create_result_str = create_def_tool._run(entity_name=entity_name, resource_type=resource_type, profiles=profiles)
            create_result = json.loads(create_result_str)
        
        # Return composite result
        return {
            "success": check_result.get("success", False) and create_result.get("success", False),
            "check_exists": check_result,
            "create_definition": create_result
        }
    
    def _set_data_value(self, entity_name: str, data_element: str, row_index: int, value: str, xlsx_path: Optional[str]) -> dict:
        """Set a patient data value."""
        tools = self.xlsx_toolkit.get_tools()
        set_value_tool = next(t for t in tools if t.name == "set_patient_data_value")
        result_str = set_value_tool._run(entity_name=entity_name, data_element=data_element, row_index=row_index, value=value)
        return json.loads(result_str)


# Tool Classes
class SetPatientTool(ResourceBuilderBaseTool):
    """Tool for setting Patient resource data."""
    
    name: str = "set_patient"
    description: str = "Set a Patient resource with common data fields for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreatePatientInput
    
    def _run(self, entity_name: str, row_index: int, given_name: Optional[str] = None,
             family_name: Optional[str] = None, birth_date: Optional[str] = None, name_use: Optional[str] = "official",
             address: Optional[str] = None, gender: Optional[str] = None, mrn: Optional[str] = None, 
             ssn: Optional[str] = None, telecom: Optional[str] = None, race: Optional[str] = None, 
             ethnicity: Optional[str] = None, language: Optional[CodeableConcept] = None, 
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Patient", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if given_name:
            results.append(self._set_data_value(entity_name, "Patient's Given Name", row_index, given_name, xlsx_path))
        if family_name:
            results.append(self._set_data_value(entity_name, "Patient's Family Name", row_index, family_name, xlsx_path))
        if birth_date:
            results.append(self._set_data_value(entity_name, "Patient's Date of Birth", row_index, birth_date, xlsx_path))
        if name_use:
            results.append(self._set_data_value(entity_name, "Patient Name Use", row_index, name_use, xlsx_path))
        if gender:
            results.append(self._set_data_value(entity_name, "Patient's Gender", row_index, gender, xlsx_path))
        if address:
            results.append(self._set_data_value(entity_name, "Patient's Primary Address", row_index, address, xlsx_path))
        if mrn:
            results.append(self._set_data_value(entity_name, "Patient MRN Identifier Value", row_index, mrn, xlsx_path))
            results.append(self._set_data_value(entity_name, "Patient MRN Identifier System", row_index, "http://your-hospital.org/identifiers/mrn", xlsx_path))
        if ssn:
            results.append(self._set_data_value(entity_name, "Patient SSN Identifier Value", row_index, ssn, xlsx_path))
            results.append(self._set_data_value(entity_name, "Patient SSN Identifier System", row_index, "http://hl7.org/fhir/sid/us-ssn", xlsx_path))
        if telecom:
            results.append(self._set_data_value(entity_name, "Patient's Telecom Number", row_index, telecom, xlsx_path))
            results.append(self._set_data_value(entity_name, "Patient's Telecom System (Type)", row_index, "phone", xlsx_path))
        if race:
            results.append(self._set_data_value(entity_name, "Patient's OMB Race Category", row_index, race, xlsx_path))
        if ethnicity:
            results.append(self._set_data_value(entity_name, "Patient's OMB Ethnicity Category", row_index, ethnicity, xlsx_path))
        if language:
            # Handle language as CodeableConcept using sheet_string method
            results.append(self._set_data_value(entity_name, "Patient's Communication Language", row_index, language.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Patient", "values_set": len(results)})


class SetPractitionerTool(ResourceBuilderBaseTool):
    """Tool for setting Practitioner resource data."""
    
    name: str = "set_practitioner"
    description: str = "Set a Practitioner resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreatePractitionerInput
    
    def _run(self, entity_name: str, row_index: int, given_name: Optional[str] = None,
             family_name: Optional[str] = None, provider_role: Optional[CodeableConcept] = None,
             provider_specialty: Optional[CodeableConcept] = None, phone_number: Optional[str] = None,
             phone_number_use: Optional[str] = "work", national_provider_identifier: Optional[str] = None,
             xlsx_path: Optional[str] = None) -> str:
        # Create Practitioner resource
        def_result = self._ensure_resource_definition(
            entity_name, "Practitioner", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if given_name:
            results.append(self._set_data_value(entity_name, "Practitioner's First Name", row_index, given_name, xlsx_path))
        if family_name:
            results.append(self._set_data_value(entity_name, "Practitioner's Last Name", row_index, family_name, xlsx_path))
        
        # Handle NPI
        if national_provider_identifier:
            results.append(self._set_data_value(entity_name, "Practitioner's National Provider Identifier", row_index, national_provider_identifier, xlsx_path))
        
        # Handle phone number
        if phone_number:
            results.append(self._set_data_value(entity_name, "Practitioner's Telecom Number", row_index, phone_number, xlsx_path))
            results.append(self._set_data_value(entity_name, "Practitioner's Telecom System (Type)", row_index, "phone", xlsx_path))
        
        # Handle phone number use
        if phone_number and phone_number_use:
            results.append(self._set_data_value(entity_name, "Practitioner's Telecom Purpose", row_index, phone_number_use, xlsx_path))
        
        # Create PractitionerRole resource
        role_entity_name = entity_name + "Role"
        role_def_result = self._ensure_resource_definition(
            role_entity_name, "PractitionerRole", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitionerrole", xlsx_path
        )
        
        role_results = []
        if role_def_result.get("success"):
            # Set role code if provider_role was provided
            if provider_role:
                role_results.append(self._set_data_value(role_entity_name, "Capacity Role Provider Serves", row_index, provider_role.sheet_string(), xlsx_path))
            
            # Set specialty if provider_specialty was provided
            if provider_specialty:
                role_results.append(self._set_data_value(role_entity_name, "Speciality of Provider", row_index, provider_specialty.sheet_string(), xlsx_path))
            
            # Set telecom information if phone_number was provided
            if phone_number:
                role_results.append(self._set_data_value(role_entity_name, "Provider's Telecom System", row_index, "phone", xlsx_path))
                role_results.append(self._set_data_value(role_entity_name, "Provider's Telecom Number", row_index, phone_number, xlsx_path))
        
        return json.dumps({
            "success": True, 
            "entity_name": entity_name, 
            "resource_type": "Practitioner", 
            "values_set": len(results),
            "role_entity_name": role_entity_name,
            "role_values_set": len(role_results),
            "role_created": role_def_result.get("success", False)
        })


class SetEncounterTool(ResourceBuilderBaseTool):
    """Tool for setting Encounter resource data."""
    
    name: str = "set_encounter"
    description: str = "Set an Encounter resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateEncounterInput
    
    def _run(self, entity_name: str, row_index: int, encounter_identifier_namespace: Optional[str] = None,
             encounter_identifier: Optional[str] = None, status: Optional[str] = None,
             encounter_class: Optional[CodeableConcept] = None, specific_encounter_type: Optional[CodeableConcept] = None,
             start_date: Optional[str] = None, end_date: Optional[str] = None,
             reason_encounter_took_place: Optional[CodeableConcept] = None,
             encounter_discharge_disposition: Optional[CodeableConcept] = None,
             encounter_note: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Encounter", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if encounter_identifier_namespace:
            results.append(self._set_data_value(entity_name, "Encounter identifier namespace", row_index, encounter_identifier_namespace, xlsx_path))
        if encounter_identifier:
            results.append(self._set_data_value(entity_name, "Encounter Identifier", row_index, encounter_identifier, xlsx_path))
        if status:
            results.append(self._set_data_value(entity_name, "Encounter Status", row_index, status, xlsx_path))
        if encounter_class:
            results.append(self._set_data_value(entity_name, "Encounter patient classification", row_index, encounter_class.sheet_string(), xlsx_path))
        if specific_encounter_type:
            results.append(self._set_data_value(entity_name, "Specific Encounter Type", row_index, specific_encounter_type.sheet_string(), xlsx_path))
        if start_date:
            results.append(self._set_data_value(entity_name, "Encounter Start Date", row_index, start_date, xlsx_path))
        if end_date:
            results.append(self._set_data_value(entity_name, "Encounter End Date", row_index, end_date, xlsx_path))
        if reason_encounter_took_place:
            results.append(self._set_data_value(entity_name, "Reason Encounter Took Place", row_index, reason_encounter_took_place.sheet_string(), xlsx_path))
        if encounter_discharge_disposition:
            results.append(self._set_data_value(entity_name, "Encounter Discharge Disposition", row_index, encounter_discharge_disposition.sheet_string(), xlsx_path))
        if encounter_note:
            results.append(self._set_data_value(entity_name, "Type of Facility Patient Discharged To", row_index, encounter_note, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Encounter", "values_set": len(results)})


class SetObservationTool(ResourceBuilderBaseTool):
    """Tool for setting Observation resource data."""
    
    name: str = "set_observation"
    description: str = "Set an Observation resource (generic - can be used for vitals, labs, etc.) for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateObservationInput
    
    def _run(self, entity_name: str, row_index: int, observation_type: str, code: Optional[str] = None,
             value: Optional[str] = None, unit: Optional[str] = None, effective_date: Optional[str] = None,
             profiles: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        if not profiles:
            profiles = "http://hl7.org/fhir/StructureDefinition/Observation"
        
        def_result = self._ensure_resource_definition(entity_name, "Observation", profiles, xlsx_path)
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if code:
            results.append(self._set_data_value(entity_name, "Code", row_index, code, xlsx_path))
        if value:
            results.append(self._set_data_value(entity_name, "Value", row_index, value, xlsx_path))
        if unit:
            results.append(self._set_data_value(entity_name, "Unit", row_index, unit, xlsx_path))
        if effective_date:
            results.append(self._set_data_value(entity_name, "Effective Date", row_index, effective_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetPractitionerRoleTool(ResourceBuilderBaseTool):
    """Tool for setting PractitionerRole resource data."""
    
    name: str = "set_practitioner_role"
    description: str = "Set a PractitionerRole resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreatePractitionerRoleInput
    
    def _run(self, entity_name: str, row_index: int, code: Optional[CodeableConcept] = None,
             specialty: Optional[CodeableConcept] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "PractitionerRole", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitionerrole", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        
        # Always set the static value "phone" for Provider's Telecom System
        results.append(self._set_data_value(entity_name, "Provider's Telecom System", row_index, "phone", xlsx_path))
        
        if code:
            results.append(self._set_data_value(entity_name, "Capacity Role Provider Serves", row_index, code.sheet_string(), xlsx_path))
        if specialty:
            results.append(self._set_data_value(entity_name, "Speciality of Provider", row_index, specialty.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "PractitionerRole", "values_set": len(results)})


class SetLocationTool(ResourceBuilderBaseTool):
    """Tool for setting Location resource data."""
    
    name: str = "set_location"
    description: str = "Set a Location resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateLocationInput
    
    def _run(self, entity_name: str, row_index: int, name: Optional[str] = None,
             address: Optional[str] = None, city: Optional[str] = None,
             state: Optional[str] = None, postal_code: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Location", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-location", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if name:
            results.append(self._set_data_value(entity_name, "Name", row_index, name, xlsx_path))
        if address:
            results.append(self._set_data_value(entity_name, "Address", row_index, address, xlsx_path))
        if city:
            results.append(self._set_data_value(entity_name, "City", row_index, city, xlsx_path))
        if state:
            results.append(self._set_data_value(entity_name, "State", row_index, state, xlsx_path))
        if postal_code:
            results.append(self._set_data_value(entity_name, "Postal Code", row_index, postal_code, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Location", "values_set": len(results)})


class SetOrganizationTool(ResourceBuilderBaseTool):
    """Tool for setting Organization resource data."""
    
    name: str = "set_organization"
    description: str = "Set an Organization resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateOrganizationInput
    
    def _run(self, entity_name: str, row_index: int, name: Optional[str] = None,
             npi: Optional[str] = None, address: Optional[str] = None,
             phone: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Organization", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if name:
            results.append(self._set_data_value(entity_name, "Name", row_index, name, xlsx_path))
        if npi:
            results.append(self._set_data_value(entity_name, "NPI", row_index, npi, xlsx_path))
        if address:
            results.append(self._set_data_value(entity_name, "Address", row_index, address, xlsx_path))
        if phone:
            results.append(self._set_data_value(entity_name, "Phone", row_index, phone, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Organization", "values_set": len(results)})


class SetImmunizationTool(ResourceBuilderBaseTool):
    """Tool for setting Immunization resource data."""
    
    name: str = "set_immunization"
    description: str = "Set an Immunization resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateImmunizationInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             reason_code: Optional[CodeableConcept] = None, vaccine_code: Optional[CodeableConcept] = None,
             occurrence_date: Optional[str] = None, primary_source: Optional[bool] = False,
             lot_number: Optional[str] = None, dose_quantity: Optional[Quantity] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Immunization", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-immunization", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Immunization current status", row_index, status, xlsx_path))
        if reason_code:
            results.append(self._set_data_value(entity_name, "Reason Immunization Adminstered", row_index, reason_code.sheet_string(), xlsx_path))
        if vaccine_code:
            results.append(self._set_data_value(entity_name, "Vaccine Code", row_index, vaccine_code.sheet_string(), xlsx_path))
        if occurrence_date:
            results.append(self._set_data_value(entity_name, "Date Vaccine Administered", row_index, occurrence_date, xlsx_path))
        if primary_source is not None:
            results.append(self._set_data_value(entity_name, "EHR Primary Source of Vaccine Record", row_index, str(primary_source).lower(), xlsx_path))
        if lot_number:
            results.append(self._set_data_value(entity_name, "Vaccine Lot Number", row_index, lot_number, xlsx_path))
        if dose_quantity:
            results.append(self._set_data_value(entity_name, "Vaccine Dose", row_index, dose_quantity.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Immunization", "values_set": len(results)})


class SetAllergyIntoleranceTool(ResourceBuilderBaseTool):
    """Tool for setting AllergyIntolerance resource data."""
    
    name: str = "set_allergy_intolerance"
    description: str = "Set an AllergyIntolerance resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateAllergyIntoleranceInput
    
    def _run(self, entity_name: str, row_index: int, code: Optional[CodeableConcept] = None,
             clinical_status: Optional[CodeableConcept] = None, verification_status: Optional[CodeableConcept] = None,
             category: Optional[str] = None, criticality: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "AllergyIntolerance", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-allergyintolerance", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if code:
            results.append(self._set_data_value(entity_name, "Code", row_index, code.sheet_string(), xlsx_path))
        if clinical_status:
            results.append(self._set_data_value(entity_name, "Clinical Status", row_index, clinical_status.sheet_string(), xlsx_path))
        if verification_status:
            results.append(self._set_data_value(entity_name, "Verification Status", row_index, verification_status.sheet_string(), xlsx_path))
        if category:
            results.append(self._set_data_value(entity_name, "Category", row_index, category, xlsx_path))
        if criticality:
            results.append(self._set_data_value(entity_name, "Criticality", row_index, criticality, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "AllergyIntolerance", "values_set": len(results)})


class SetProcedureTool(ResourceBuilderBaseTool):
    """Tool for setting Procedure resource data."""
    
    name: str = "set_procedure"
    description: str = "Set a Procedure resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateProcedureInput
    
    def _run(self, entity_name: str, row_index: int, code: Optional[CodeableConcept] = None,
             status: Optional[str] = None, performed_date: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Procedure", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Procedure Event Status", row_index, status, xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Procedure code", row_index, code.sheet_string(), xlsx_path))
        if performed_date:
            results.append(self._set_data_value(entity_name, "Procedure's Performed Datetime", row_index, performed_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Procedure", "values_set": len(results)})


class SetEncounterDiagnosisConditionTool(ResourceBuilderBaseTool):
    """Tool for setting Encounter Diagnosis Condition resource data."""
    
    name: str = "set_encounter_diagnosis_condition"
    description: str = "Set an Encounter Diagnosis Condition resource (for conditions assigned during an encounter) for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateEncounterDiagnosisConditionInput
    
    def _run(self, entity_name: str, row_index: int, code: Optional[CodeableConcept] = None,
             clinical_status: Optional[CodeableConcept] = None, verification_status: Optional[CodeableConcept] = None,
             onset_date: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Condition", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        
        # Set fixed category for encounter-diagnosis
        category = CodeableConcept(
            system="http://terminology.hl7.org/CodeSystem/condition-category",
            code="encounter-diagnosis"
        )
        results.append(self._set_data_value(entity_name, "Condition Category", row_index, category.sheet_string(), xlsx_path))
        
        if clinical_status:
            results.append(self._set_data_value(entity_name, "Condition Clinical Status", row_index, clinical_status.sheet_string(), xlsx_path))
        if verification_status:
            results.append(self._set_data_value(entity_name, "Condition Verification Status", row_index, verification_status.sheet_string(), xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Condition Code", row_index, code.sheet_string(), xlsx_path))
        if onset_date:
            results.append(self._set_data_value(entity_name, "Condition Onset Date", row_index, onset_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Condition", "values_set": len(results)})


class SetHealthProblemConditionTool(ResourceBuilderBaseTool):
    """Tool for setting Health Problem/Concern Condition resource data."""
    
    name: str = "set_health_problem_condition"
    description: str = "Set a Health Problem or Health Concern Condition resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateHealthProblemConditionInput
    
    def _run(self, entity_name: str, row_index: int, code: Optional[CodeableConcept] = None,
             clinical_status: Optional[CodeableConcept] = None, verification_status: Optional[CodeableConcept] = None,
             category_code: Literal["problem-list-item", "health-concern"] = "problem-list-item",
             onset_date: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Condition", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-problems-health-concerns", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        
        # Set category based on provided category_code
        category = CodeableConcept(
            system="http://terminology.hl7.org/CodeSystem/condition-category",
            code=category_code
        )
        results.append(self._set_data_value(entity_name, "Condition Category", row_index, category.sheet_string(), xlsx_path))
        
        if clinical_status:
            results.append(self._set_data_value(entity_name, "Condition Clinical Status", row_index, clinical_status.sheet_string(), xlsx_path))
        if verification_status:
            results.append(self._set_data_value(entity_name, "Condition Verification Status", row_index, verification_status.sheet_string(), xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Condition Code", row_index, code.sheet_string(), xlsx_path))
        if onset_date:
            results.append(self._set_data_value(entity_name, "Condition Onset Date", row_index, onset_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Condition", "values_set": len(results)})


class SetMedicationRequestTool(ResourceBuilderBaseTool):
    """Tool for setting MedicationRequest resource data."""
    
    name: str = "set_medication_request"
    description: str = "Set a MedicationRequest resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateMedicationRequestInput
    
    def _run(self, entity_name: str, row_index: int, medication_code: Optional[CodeableConcept ] = None,
             status: Optional[str] = None, intent: Optional[str] = None,
             authored_on: Optional[str] = None, dosage_instruction: Optional[str] = None,
             medication_route: Optional[CodeableConcept] = None, medication_dosage: Optional[Quantity] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "MedicationRequest", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Medication Request Status", row_index, status, xlsx_path))
        if medication_code:
            results.append(self._set_data_value(entity_name, "Medication Code", row_index, medication_code.sheet_string(), xlsx_path))
        if status:
            results.append(self._set_data_value(entity_name, "Medication Request Status", row_index, status, xlsx_path))
        if authored_on:
            results.append(self._set_data_value(entity_name, "Medication Date", row_index, authored_on, xlsx_path))
        if dosage_instruction:
            results.append(self._set_data_value(entity_name, "Medication Dosage Instructions", row_index, dosage_instruction, xlsx_path))
        if medication_route:
            results.append(self._set_data_value(entity_name, "Medication Route", row_index, medication_route.sheet_string(), xlsx_path))
        if medication_dosage:
            results.append(self._set_data_value(entity_name, "Medication Dosage", row_index, medication_dosage.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "MedicationRequest", "values_set": len(results)})


class SetDiagnosticReportTool(ResourceBuilderBaseTool):
    """Tool for setting DiagnosticReport resource data."""
    
    name: str = "set_diagnostic_report"
    description: str = "Set a DiagnosticReport resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateDiagnosticReportInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             code: Optional[CodeableConcept] = None, effective_date: Optional[str] = None,
             issued_date: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "DiagnosticReport", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Diagnostic Report's Status", row_index, status, xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Diagnostic Report Order Code", row_index, code.sheet_string(), xlsx_path))
        if effective_date:
            results.append(self._set_data_value(entity_name, "Diagnostic Report Effective Datetime", row_index, effective_date, xlsx_path))
        if issued_date:
            results.append(self._set_data_value(entity_name, "Diagnostic Report Issued Datetime", row_index, issued_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "DiagnosticReport", "values_set": len(results)})


class SetLaboratoryResultTool(ResourceBuilderBaseTool):
    """Tool for setting Laboratory Result Observation resource data."""
    
    name: str = "set_laboratory_result"
    description: str = "Set a Laboratory Result Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateLaboratoryResultInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             code: Optional[CodeableConcept] = None, category: Optional[CodeableConcept] = None,
             record_date: Optional[str] = None, value: Optional[Quantity] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Laboratory Result Status", row_index, status, xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Laboratory Test Code (LOINC)", row_index, code.sheet_string(), xlsx_path))
        if category:
            results.append(self._set_data_value(entity_name, "Laboratory Result Category", row_index, category.sheet_string(), xlsx_path))
        if record_date:
            results.append(self._set_data_value(entity_name, "Laboratory Result RecordedDate", row_index, record_date, xlsx_path))
        if value:
            results.append(self._set_data_value(entity_name, "Laboratory Result Value", row_index, value.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetVitalSignTool(ResourceBuilderBaseTool):
    """Tool for setting Vital Sign Observation resource data."""
    
    name: str = "set_vital_sign"
    description: str = "Set a Vital Sign Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateVitalSignInput
    
    def _run(self, entity_name: str, row_index: int, type: Optional[CodeableConcept] = None,
             effective_datetime: Optional[str] = None, value: Optional[Quantity] = None,
             status: Optional[str] = None, category: Optional[CodeableConcept] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/StructureDefinition/vitalsigns", xlsx_path, value_type="Quantity"
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if type:
            results.append(self._set_data_value(entity_name, "Vital Sign Type", row_index, type.sheet_string(), xlsx_path))
        if effective_datetime:
            results.append(self._set_data_value(entity_name, "Vital Sign effectiveDatetime", row_index, effective_datetime, xlsx_path))
        if value:
            results.append(self._set_data_value(entity_name, "Vital Sign Value", row_index, value.sheet_string(), xlsx_path))
        if status:
            results.append(self._set_data_value(entity_name, "Vital Sign Status", row_index, status, xlsx_path))
        if category:
            results.append(self._set_data_value(entity_name, "Vital Sign Category", row_index, category.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetHeightTool(ResourceBuilderBaseTool):
    """Tool for setting Height Observation resource data."""
    
    name: str = "set_height"
    description: str = "Set a Height Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateHeightInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for height (LOINC code 8302-2)
        height_code = CodeableConcept(system="http://loinc.org", code="8302-2", display="Body height")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, height_code, effective_datetime, value, xlsx_path)


class SetWeightTool(ResourceBuilderBaseTool):
    """Tool for setting Weight Observation resource data."""
    
    name: str = "set_weight"
    description: str = "Set a Weight Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateWeightInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for weight (LOINC code 29463-7)
        weight_code = CodeableConcept(system="http://loinc.org", code="29463-7", display="Body weight")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, weight_code, effective_datetime, value, xlsx_path)


class SetBodyTemperatureTool(ResourceBuilderBaseTool):
    """Tool for setting Body Temperature Observation resource data."""
    
    name: str = "set_body_temperature"
    description: str = "Set a Body Temperature Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateBodyTemperatureInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for body temperature (LOINC code 8310-5)
        temp_code = CodeableConcept(system="http://loinc.org", code="8310-5", display="Body temperature")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, temp_code, effective_datetime, value, xlsx_path)


class SetRespiratoryRateTool(ResourceBuilderBaseTool):
    """Tool for setting Respiratory Rate Observation resource data."""
    
    name: str = "set_respiratory_rate"
    description: str = "Set a Respiratory Rate Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateRespiratoryRateInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for respiratory rate (LOINC code 9279-1)
        resp_rate_code = CodeableConcept(system="http://loinc.org", code="9279-1", display="Respiratory rate")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, resp_rate_code, effective_datetime, value, xlsx_path)


class SetHeartRateTool(ResourceBuilderBaseTool):
    """Tool for setting Heart Rate Observation resource data."""
    
    name: str = "set_heart_rate"
    description: str = "Set a Heart Rate Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateHeartRateInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for heart rate (LOINC code 8867-4)
        heart_rate_code = CodeableConcept(system="http://loinc.org", code="8867-4", display="Heart rate")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, heart_rate_code, effective_datetime, value, xlsx_path)


class SetOxygenConcentrationTool(ResourceBuilderBaseTool):
    """Tool for setting Oxygen Concentration Observation resource data."""
    
    name: str = "set_oxygen_concentration"
    description: str = "Set an Oxygen Concentration Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateOxygenConcentrationInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             value: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for oxygen concentration (LOINC code 3150-0)
        oxygen_concentration_code = CodeableConcept(system="http://loinc.org", code="3150-0", display="Inhaled oxygen concentration")
        
        # Call the base SetVitalSignTool
        vital_sign_tool = SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit)
        return vital_sign_tool._run(entity_name, row_index, oxygen_concentration_code, effective_datetime, value, xlsx_path)


class SetBloodPressureTool(ResourceBuilderBaseTool):
    """Tool for setting Blood Pressure Observation resource data."""
    
    name: str = "set_blood_pressure"
    description: str = "Set a Blood Pressure Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateBloodPressureInput
    
    def _run(self, entity_name: str, row_index: int, effective_datetime: Optional[str] = None,
             systolic_value: Optional[Quantity] = None, diastolic_value: Optional[Quantity] = None,
             xlsx_path: Optional[str] = None) -> str:
        # Create predefined CodeableConcept for blood pressure (LOINC code 85354-9)
        bp_code = CodeableConcept(system="http://loinc.org", code="85354-9", display="Blood pressure")
        
        # Create predefined CodeableConcepts for systolic and diastolic codes
        systolic_code = CodeableConcept(system="http://loinc.org", code="8480-6", display="Systolic blood pressure")
        diastolic_code = CodeableConcept(system="http://loinc.org", code="8462-4", display="Diastolic blood pressure")
        
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/StructureDefinition/bp", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        # Set the blood pressure type code
        results.append(self._set_data_value(entity_name, "Vital Sign Type", row_index, bp_code.sheet_string(), xlsx_path))
        
        if effective_datetime:
            results.append(self._set_data_value(entity_name, "Vital Sign effectiveDatetime", row_index, effective_datetime, xlsx_path))
        
        # Set systolic blood pressure with code and value
        if systolic_value:
            results.append(self._set_data_value(entity_name, "Vital Sign Blood Pressure Systolic BP Code", row_index, systolic_code.sheet_string(), xlsx_path))
            results.append(self._set_data_value(entity_name, "Vital Sign Blood Pressure Systolic BP", row_index, systolic_value.sheet_string(), xlsx_path))
        
        # Set diastolic blood pressure with code and value
        if diastolic_value:
            results.append(self._set_data_value(entity_name, "Vital Sign Blood Pressure Diastolic BP Code", row_index, diastolic_code.sheet_string(), xlsx_path))
            results.append(self._set_data_value(entity_name, "Vital Sign Blood Pressure Diastolic BP", row_index, diastolic_value.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetPulseOximetryTool(ResourceBuilderBaseTool):
    """Tool for setting Pulse Oximetry Observation resource data."""
    
    name: str = "set_pulse_oximetry"
    description: str = "Set a Pulse Oximetry Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreatePulseOximetryInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             effective_date: Optional[str] = None, flow_rate: Optional[Quantity] = None,
             concentration: Optional[Quantity] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/StructureDefinition/oxygensat", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Pulse Oximetry Status", row_index, status, xlsx_path))
        results.append(self._set_data_value(entity_name, "Pulse Oximetry Code 0", row_index, "http://loinc.org^59408-5", xlsx_path))
        results.append(self._set_data_value(entity_name, "Pulse Oximetry Code 1", row_index, "http://loinc.org^2708-6", xlsx_path))
        if effective_date:
            results.append(self._set_data_value(entity_name, "Pulse Oximetry Effective Date", row_index, effective_date, xlsx_path))
        if flow_rate:
            results.append(self._set_data_value(entity_name, "Pulse Oximetry FlowRate", row_index, flow_rate.sheet_string(), xlsx_path))
        if concentration:
            results.append(self._set_data_value(entity_name, "Pulse Oximetry Concentration", row_index, concentration.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetPediatricBmiForAgeTool(ResourceBuilderBaseTool):
    """Tool for setting Pediatric BMI for Age Observation resource data."""
    
    name: str = "set_pediatric_bmi_for_age"
    description: str = "Set a Pediatric BMI for Age Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreatePediatricBmiForAgeInput
    
    def _run(self, entity_name: str, row_index: int, value: Optional[str] = None,
             effective_date: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/StructureDefinition/pediatric-bmi-for-age", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if value:
            results.append(self._set_data_value(entity_name, "Value", row_index, value, xlsx_path))
        if effective_date:
            results.append(self._set_data_value(entity_name, "Effective Date", row_index, effective_date, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetDeviceTool(ResourceBuilderBaseTool):
    """Tool for setting Device resource data."""
    
    name: str = "set_device"
    description: str = "Set a Device resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateDeviceInput
    
    def _run(self, entity_name: str, row_index: int, identifier: Optional[str] = None,
             carrier_hrf: Optional[str] = None, manufacture_date: Optional[str] = None,
             expiration_date: Optional[str] = None, lot_number: Optional[str] = None,
             serial_number: Optional[str] = None, type: Optional[CodeableConcept] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Device", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-implantable-device", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if identifier:
            results.append(self._set_data_value(entity_name, "Implantable Device Identifier", row_index, identifier, xlsx_path))
        if carrier_hrf:
            results.append(self._set_data_value(entity_name, "Implantable Device Identifier Human Readable Format", row_index, carrier_hrf, xlsx_path))
        if manufacture_date:
            results.append(self._set_data_value(entity_name, "Implantable Device Manufacture Date", row_index, manufacture_date, xlsx_path))
        if expiration_date:
            results.append(self._set_data_value(entity_name, "Implantable Device Expirateion Date", row_index, expiration_date, xlsx_path))
        if lot_number:
            results.append(self._set_data_value(entity_name, "Implantable Device Lot Number", row_index, lot_number, xlsx_path))
        if serial_number:
            results.append(self._set_data_value(entity_name, "Implantable Device Serial Number", row_index, serial_number, xlsx_path))
        if type:
            results.append(self._set_data_value(entity_name, "Implantable Device Type", row_index, type.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Device", "values_set": len(results)})


class SetSmokingStatusTool(ResourceBuilderBaseTool):
    """Tool for setting Smoking Status Observation resource data."""
    
    name: str = "set_smoking_status"
    description: str = "Set a Smoking Status Observation resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateSmokingStatusInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             code: Optional[CodeableConcept] = None, category: Optional[CodeableConcept] = None,
             effective_date: Optional[str] = None, value: Optional[CodeableConcept] = None,
             xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "Observation", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-smokingstatus", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "SmokingStatus status", row_index, status, xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "SmokingStatus Code", row_index, code.sheet_string(), xlsx_path))
        if category:
            results.append(self._set_data_value(entity_name, "SmokingStatus Category", row_index, category.sheet_string(), xlsx_path))
        if effective_date:
            results.append(self._set_data_value(entity_name, "Pulse Oximetry Effective Date", row_index, effective_date, xlsx_path))
        if value:
            results.append(self._set_data_value(entity_name, "Smoking Status Value", row_index, value.sheet_string(), xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "Observation", "values_set": len(results)})


class SetServiceRequestTool(ResourceBuilderBaseTool):
    """Tool for setting ServiceRequest resource data."""
    
    name: str = "set_service_request"
    description: str = "Set a ServiceRequest resource for a specific row_index (patient)"
    args_schema: Type[BaseModel] = CreateServiceRequestInput
    
    def _run(self, entity_name: str, row_index: int, status: Optional[str] = None,
             intent: Optional[str] = None, code: Optional[CodeableConcept] = None,
             occurrence_date_time: Optional[str] = None, xlsx_path: Optional[str] = None) -> str:
        def_result = self._ensure_resource_definition(
            entity_name, "ServiceRequest", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-servicerequest", xlsx_path
        )
        if not def_result.get("success"):
            return json.dumps(def_result)
        
        results = []
        if status:
            results.append(self._set_data_value(entity_name, "Service Request Status", row_index, status, xlsx_path))
        if intent:
            results.append(self._set_data_value(entity_name, "Service Request Intent", row_index, intent, xlsx_path))
        if code:
            results.append(self._set_data_value(entity_name, "Service Request Code", row_index, code.sheet_string(), xlsx_path))
        if occurrence_date_time:
            results.append(self._set_data_value(entity_name, "Sercice Request Occurrence Date", row_index, occurrence_date_time, xlsx_path))
        
        return json.dumps({"success": True, "entity_name": entity_name, "resource_type": "ServiceRequest", "values_set": len(results)})


# Toolkit Class
class FhirSheetsResourceBuilderToolkit(BaseToolkit):
    """Toolkit for high-level FHIR resource creation."""
    
    xlsx_toolkit: FhirSheetsXlsxToolkit = Field(default=FhirSheetsXlsxToolkit(), description="Instance of FhirSheetsXlsxToolkit")
    def __init__(self, xlsx_toolkit: Optional[FhirSheetsXlsxToolkit] = None):
        """Initialize the toolkit."""
        super().__init__()
        self.xlsx_toolkit = xlsx_toolkit or FhirSheetsXlsxToolkit()
    
    def get_tools(self) -> List[BaseTool]:
        """Get all resource builder tools plus the underlying XLSX toolkit tools."""
        # Get the low-level XLSX tools
        xlsx_tools = self.xlsx_toolkit.get_tools()
        
        # Get the high-level resource builder tools
        resource_builder_tools = [
            SetPatientTool(xlsx_toolkit=self.xlsx_toolkit),
            SetPractitionerTool(xlsx_toolkit=self.xlsx_toolkit),
            SetEncounterTool(xlsx_toolkit=self.xlsx_toolkit),
            SetObservationTool(xlsx_toolkit=self.xlsx_toolkit),
            SetPractitionerRoleTool(xlsx_toolkit=self.xlsx_toolkit),
            SetLocationTool(xlsx_toolkit=self.xlsx_toolkit),
            SetOrganizationTool(xlsx_toolkit=self.xlsx_toolkit),
            SetImmunizationTool(xlsx_toolkit=self.xlsx_toolkit),
            SetAllergyIntoleranceTool(xlsx_toolkit=self.xlsx_toolkit),
            SetProcedureTool(xlsx_toolkit=self.xlsx_toolkit),
            SetEncounterDiagnosisConditionTool(xlsx_toolkit=self.xlsx_toolkit),
            SetHealthProblemConditionTool(xlsx_toolkit=self.xlsx_toolkit),
            SetMedicationRequestTool(xlsx_toolkit=self.xlsx_toolkit),
            SetDiagnosticReportTool(xlsx_toolkit=self.xlsx_toolkit),
            SetLaboratoryResultTool(xlsx_toolkit=self.xlsx_toolkit),
            SetVitalSignTool(xlsx_toolkit=self.xlsx_toolkit),
            SetHeightTool(xlsx_toolkit=self.xlsx_toolkit),
            SetWeightTool(xlsx_toolkit=self.xlsx_toolkit),
            SetBodyTemperatureTool(xlsx_toolkit=self.xlsx_toolkit),
            SetRespiratoryRateTool(xlsx_toolkit=self.xlsx_toolkit),
            SetHeartRateTool(xlsx_toolkit=self.xlsx_toolkit),
            SetOxygenConcentrationTool(xlsx_toolkit=self.xlsx_toolkit),
            SetBloodPressureTool(xlsx_toolkit=self.xlsx_toolkit),
            SetPulseOximetryTool(xlsx_toolkit=self.xlsx_toolkit),
            SetPediatricBmiForAgeTool(xlsx_toolkit=self.xlsx_toolkit),
            SetDeviceTool(xlsx_toolkit=self.xlsx_toolkit),
            SetSmokingStatusTool(xlsx_toolkit=self.xlsx_toolkit),
            SetServiceRequestTool(xlsx_toolkit=self.xlsx_toolkit),
        ]
        
        # Return combined list: XLSX tools first, then resource builder tools
        return xlsx_tools + resource_builder_tools
