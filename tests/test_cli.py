import datetime
import pathlib
import json
from typing import Iterable, Dict, List
from src.fhir_sheets.core import conversion
from src.fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from src.fhir_sheets.core.conversion import create_singular_resource
from src.fhir_sheets.core.model.cohort_data_entity import CohortData
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition
from src.fhir_sheets.core.model.resource_link_entity import ResourceLink
from src.fhir_sheets.cli.main import main
import src.fhir_sheets.core.conversion

TOP_DIR = pathlib.Path(__file__).parent.parent / "samples"


def test_congential_hyperthyrodism_excel_conversion(tmp_path):
    input_file = (
        TOP_DIR
        / "Congenital_Hyperthyrodism/Congenital_Hyperthyrodism_Fhir_Cohort_Import_Template.xlsx"
    ).__str__()
    main(input_file, tmp_path)

    json_files = list(tmp_path.glob("*.json"))
    json_file = json_files[0]
    with json_file.open("r") as file:
        fhir_bundle = json.load(file)

    assert fhir_bundle["resourceType"] == "Bundle"
    assert fhir_bundle["type"] == "transaction"

def test_congential_hyperthyrodism_excel_conversion_preview_mode(tmp_path):
    input_file = (
        TOP_DIR
        / "Congenital_Hyperthyrodism/Congenital_Hyperthyrodism_Fhir_Cohort_Import_Template.xlsx"
    ).__str__()
    main(input_file, tmp_path, FhirSheetsConfiguration({"preview_mode": True}))

    json_files = list(tmp_path.glob("*.json"))
    json_file = json_files[0]
    with json_file.open("r") as file:
        fhir_bundle = json.load(file)

    assert fhir_bundle["resourceType"] == "Bundle"
    assert fhir_bundle["type"] == "transaction"
    
    primaryEncounter = [entry["resource"] for entry in fhir_bundle["entry"] if entry["resource"]["resourceType"] == 'Encounter'][0]
    assert primaryEncounter
    assert primaryEncounter["subject"] == { 'reference': 'Patient/PrimaryPatient' }

def test_singleton_resource_creation():
    resource_definitions = [
        {
            "Entity Name": "PrimaryEncounter",
            "ResourceType": "Encounter",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"
            ],
            
        },
        {
            "Entity Name": "PrimaryPatient",
            "ResourceType": "Patient",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
            ],
            
        },
        {
            "Entity Name": "Mother",
            "ResourceType": "RelatedPerson",
            "Profile(s)": None,
            
        },
        {
            "Entity Name": "HearingScreening",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            
        },
        {
            "Entity Name": "CMVTest",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            
        },
        {
            "Entity Name": "Ultrasound",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            
        },
        {
            "Entity Name": "Diagnosis",
            "ResourceType": "Condition",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"
            ],
            
        },
        {
            "Entity Name": "Valganciclovir",
            "ResourceType": "MedicationRequest",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"
            ],
            
        },
    ]
    resource_links = [
        {
            "OriginResource": "PrimaryEncounter",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "Mother",
            "ReferencePath": "patient",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "HearingScreening",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "HearingScreening",
            "ReferencePath": "Encounter",
            "DestinationResource": "PrimaryEncounter",
        },
        {
            "OriginResource": "CMVTest",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "CMVTest",
            "ReferencePath": "Encounter",
            "DestinationResource": "PrimaryEncounter",
        },
        {
            "OriginResource": "Ultrasound",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "Ultrasound",
            "ReferencePath": "Encounter",
            "DestinationResource": "PrimaryEncounter",
        },
        {
            "OriginResource": "Diagnosis",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
        {
            "OriginResource": "Valganciclovir",
            "ReferencePath": "Subject",
            "DestinationResource": "PrimaryPatient",
        },
    ]
    headers = [
        {
            "fieldName": "Patient's OMB Race Category",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.extension[Race].ombCategory",
            "valueType": None,
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-omb-race-category.html",
        },
        {
            "fieldName": "Patient's OMB Ethnicity Category",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.extension[Ethnicity].ombCategory.value",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-omb-ethnicity-category.html",
        },
        {
            "fieldName": "Patient's Sex at Birth",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.extension[Birthsex].value",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-birthsex.html",
        },
        {
            "fieldName": "Patient Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier.[0].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient Identifier System",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier.[0].system",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient MRN Identifier System",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier[type=MRN].system",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient MRN Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier[type=MRN].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient SSN Identifier System",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier[type=SSN].system",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient SSN Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.identifier[type=SSN].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Given Name",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.name.[0].given",
            "valueType": "string[]",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Family Name",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.name.[0].family",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient name Use (Type)",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.name[0].use",
            "valueType": "code",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Telecom System (Type)",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.telecom.[0].system",
            "valueType": "string",
            "valueSets": "https://hl7.org/fhir/R4/valueset-contact-point-system.html",
        },
        {
            "fieldName": "Patient's Telecom Number",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.telecom.[0].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Telecom Purpose",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.telecom.[0].use",
            "valueType": "string",
            "valueSets": "https://hl7.org/fhir/R4/valueset-contact-point-use.html",
        },
        {
            "fieldName": "Patient's Gender",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.gender",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-administrative-gender.html",
        },
        {
            "fieldName": "Patient's Date of Birth",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.birthDate",
            "valueType": "date",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Primary Address",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.address.[0]",
            "valueType": "Address",
            "valueSets": None,
        },
        {
            "fieldName": "Patient's Communication Language",
            "entityName": "PrimaryPatient",
            "jsonPath": "Patient.communication.[0].language",
            "valueType": "CodeableConcept",
            "valueSets": None,
        },
        {
            "fieldName": "Encounter identifier namespace",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.identifier.[0].system",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Encounter Identifier",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.identifier.[0].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Encounter Status",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.status",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-encounter-status.html",
        },
        {
            "fieldName": "Encounter patient classification",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.class",
            "valueType": "Coding",
            "valueSets": "https://hl7.org/fhir/R4/v3/ActEncounterCode/vs.html",
        },
        {
            "fieldName": "Specific Encounter Type",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.type.[0]",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-encounter-type.html",
        },
        {
            "fieldName": "Encounter Start Date",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.period.start",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Encounter End Date",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.period.end",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Type of Facility Patient Discharged To",
            "entityName": "PrimaryEncounter",
            "jsonPath": "Encounter.hospitalization.dischargeDisposition",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/R4/valueset-encounter-discharge-disposition.html",
        },
        {
            "fieldName": "Mother identifier namespace",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.identifier.[0].system",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Mother identifier",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.identifier.[0].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Mother Relationship Code",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.relationship.[0]",
            "valueType": "CodeableConcept",
            "valueSets": "https://www.hl7.org/fhir/r4/valueset-relatedperson-relationshiptype.html",
        },
        {
            "fieldName": "Mother's Given Name",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.name.[0].given",
            "valueType": "string[]",
            "valueSets": None,
        },
        {
            "fieldName": "Mother's Family Name",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.name.[0].family",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Mother's name Use (Type)",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.name[0].use",
            "valueType": "code",
            "valueSets": None,
        },
        {
            "fieldName": "Mother's Telecom System (Type)",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.telecom.[0].system",
            "valueType": "string",
            "valueSets": "https://hl7.org/fhir/R4/valueset-contact-point-system.html",
        },
        {
            "fieldName": "Mother's Telecom Number",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.telecom.[0].value",
            "valueType": "string",
            "valueSets": None,
        },
        {
            "fieldName": "Mother's Telecom Purpose",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.telecom.[0].use",
            "valueType": "string",
            "valueSets": "https://hl7.org/fhir/R4/valueset-contact-point-use.html",
        },
        {
            "fieldName": "Mother's Gender",
            "entityName": "Mother",
            "jsonPath": "RelatedPerson.gender",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-administrative-gender.html",
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "HearingScreening",
            "jsonPath": "Procedure.status",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "HearingScreening",
            "jsonPath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "HearingScreening",
            "jsonPath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "CMVTest",
            "jsonPath": "Procedure.status",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "CMVTest",
            "jsonPath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "CMVTest",
            "jsonPath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "Ultrasound",
            "jsonPath": "Procedure.status",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "Ultrasound",
            "jsonPath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "Ultrasound",
            "jsonPath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Condition Clinical Status",
            "entityName": "Diagnosis",
            "jsonPath": "Condition.clinicalStatus",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/R4/valueset-condition-clinical.html",
        },
        {
            "fieldName": "Condition Verification Status",
            "entityName": "Diagnosis",
            "jsonPath": "Condition.verificationStatus",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/R4/valueset-condition-ver-status.html",
        },
        {
            "fieldName": "Condition Category",
            "entityName": "Diagnosis",
            "jsonPath": "Condition.category.[0]",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-condition-category.html",
        },
        {
            "fieldName": "Condition Code",
            "entityName": "Diagnosis",
            "jsonPath": "Condition.code",
            "valueType": "CodeableConcept",
            "valueSets": None,
        },
        {
            "fieldName": "Condition Onset Date",
            "entityName": "Diagnosis",
            "jsonPath": "Condition.onsetDateTime",
            "valueType": "datetime",
            "valueSets": None,
        },
        {
            "fieldName": "Medication Request Status",
            "entityName": "Valganciclovir",
            "jsonPath": "MedicationRequest.status",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-medicationrequest-status.html",
        },
        {
            "fieldName": "Medication Request Intent",
            "entityName": "Valganciclovir",
            "jsonPath": "MedicationRequest.intent",
            "valueType": "code",
            "valueSets": "https://hl7.org/fhir/R4/valueset-medicationrequest-intent.html",
        },
        {
            "fieldName": "Medication Code",
            "entityName": "Valganciclovir",
            "jsonPath": "MedicationRequest.medicationCodeableConcept",
            "valueType": "CodeableConcept",
            "valueSets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-medication-codes.html",
        },
        {
            "fieldName": "Medication Date",
            "entityName": "Valganciclovir",
            "jsonPath": "MedicationRequest.authoredOn",
            "valueType": "dateTime",
            "valueSets": None,
        },
        {
            "fieldName": "Medication Dosage Instructions",
            "entityName": "Valganciclovir",
            "jsonPath": "MedicationRequest.dosageInstruction.[0].text",
            "valueType": "string",
            "valueSets": None,
        },
    ]
    patients = [
        {
            ("PrimaryPatient", "Patient's OMB Race Category"): "Asian ",
            (
                "PrimaryPatient",
                "Patient's OMB Ethnicity Category",
            ): "Not Hispanic or Latino ",
            ("PrimaryPatient", "Patient's Sex at Birth"): "M",
            ("PrimaryPatient", "Patient Identifier Value"): 7890123,
            (
                "PrimaryPatient",
                "Patient Identifier System",
            ): "http://hospital.smarthealthit.org",
            (
                "PrimaryPatient",
                "Patient MRN Identifier System",
            ): "urn:mrn:http://hl7.org/fhir/sid/us-mrn",
            ("PrimaryPatient", "Patient MRN Identifier Value"): 68392077,
            (
                "PrimaryPatient",
                "Patient SSN Identifier System",
            ): "http://hl7.org/fhir/sid/us-ssn",
            ("PrimaryPatient", "Patient SSN Identifier Value"): "456-78-9012",
            ("PrimaryPatient", "Patient's Given Name"): "Ethan",
            ("PrimaryPatient", "Patient's Family Name"): "Crosswell",
            ("PrimaryPatient", "Patient name Use (Type)"): "usual ",
            ("PrimaryPatient", "Patient's Telecom System (Type)"): "phone",
            ("PrimaryPatient", "Patient's Telecom Number"): "777-777-7777",
            ("PrimaryPatient", "Patient's Telecom Purpose"): "home",
            ("PrimaryPatient", "Patient's Gender"): "male",
            ("PrimaryPatient", "Patient's Date of Birth"): datetime.datetime(
                2019, 5, 6, 0, 0
            ),
            (
                "PrimaryPatient",
                "Patient's Primary Address",
            ): "42 Elmwood Drive^Boulder^Boulder^90302^CO^US",
            (
                "PrimaryPatient",
                "Patient's Communication Language",
            ): "urn:ietf:bcp:47^en^English",
            (
                "PrimaryEncounter",
                "Encounter identifier namespace",
            ): "urn:example:healthcare:system",
            ("PrimaryEncounter", "Encounter Identifier"): 3456,
            ("PrimaryEncounter", "Encounter Status"): "finished",
            (
                "PrimaryEncounter",
                "Encounter patient classification",
            ): "http://terminology.hl7.org/CodeSystem/v3-ActCode^IMP^inpatient encounter",
            (
                "PrimaryEncounter",
                "Specific Encounter Type",
            ): "http://hl7.org/fhir/sid/icd-10^O80^Single spontaneous delivery",
            ("PrimaryEncounter", "Encounter Start Date"): datetime.datetime(
                2019, 5, 6, 11, 1, 23
            ),
            ("PrimaryEncounter", "Encounter End Date"): datetime.datetime(
                2019, 5, 6, 16, 6, 37
            ),
            (
                "PrimaryEncounter",
                "Type of Facility Patient Discharged To",
            ): "http://terminology.hl7.org/CodeSystem/discharge-disposition^home^Home",
            ("Mother", "Mother identifier namespace"): "urn:example:healthcare:system",
            ("Mother", "Mother identifier"): 4567,
            (
                "Mother",
                "Mother Relationship Code",
            ): "http://terminology.hl7.org/CodeSystem/v3-RoleCode^MTH^Mother",
            ("Mother", "Mother's Given Name"): "Lillian",
            ("Mother", "Mother's Family Name"): "Crosswell",
            ("Mother", "Mother's name Use (Type)"): "usual ",
            ("Mother", "Mother's Telecom System (Type)"): "phone",
            ("Mother", "Mother's Telecom Number"): "888-888-8888",
            ("Mother", "Mother's Telecom Purpose"): "home",
            ("Mother", "Mother's Gender"): "female",
            ("HearingScreening", "Procedure Event Status"): "completed",
            (
                "HearingScreening",
                "Procedure code",
            ): "http://www.ama-assn.org/go/cpt^92558^Automated evoked otoacoustic emissions screening",
            ("HearingScreening", "Procedure's Performed Datetime"): datetime.datetime(
                2019, 5, 7, 0, 0
            ),
            ("CMVTest", "Procedure Event Status"): "completed",
            (
                "CMVTest",
                "Procedure code",
            ): "http://www.ama-assn.org/go/cpt^87496^Cytomegalovirus detection by amplified nucleic acid probe technique",
            ("CMVTest", "Procedure's Performed Datetime"): datetime.datetime(
                2019, 5, 8, 0, 0
            ),
            ("Ultrasound", "Procedure Event Status"): "completed",
            (
                "Ultrasound",
                "Procedure code",
            ): "http://www.ama-assn.org/go/cpt^70551^MRI scan of brain without contrast",
            ("Ultrasound", "Procedure's Performed Datetime"): datetime.datetime(
                2018, 4, 15, 0, 0
            ),
            (
                "Diagnosis",
                "Condition Clinical Status",
            ): "http://terminology.hl7.org/CodeSystem/condition-clinical^active^Active",
            (
                "Diagnosis",
                "Condition Verification Status",
            ): "http://terminology.hl7.org/CodeSystem/condition-ver-status^confirmed^Confirmed",
            (
                "Diagnosis",
                "Condition Category",
            ): "http://hl7.org/fhir/us/core/CodeSystem/condition-category^health-concern^Health Concern",
            (
                "Diagnosis",
                "Condition Code",
            ): "http://hl7.org/fhir/sid/icd-10^E03.1^congenital hypothyroidism without goitre",
            ("Diagnosis", "Condition Onset Date"): datetime.datetime(2019, 5, 6, 0, 0),
            ("Valganciclovir", "Medication Request Status"): "active",
            ("Valganciclovir", "Medication Request Intent"): "order",
            (
                "Valganciclovir",
                "Medication Code",
            ): "http://www.nlm.nih.gov/research/umls/rxnorm^275891^valganciclovir",
            ("Valganciclovir", "Medication Date"): datetime.datetime(2019, 5, 6, 0, 0),
            (
                "Valganciclovir",
                "Medication Dosage Instructions",
            ): "0.2 mg/kg/dose, given twice daily",
        }
    ]
    singleton_resource_name = resource_definitions[0]['Entity Name']
    resource_definitions_class: List[ResourceDefinition] = [ResourceDefinition.from_dict(x) for x in resource_definitions]
    resource_links_class = [ResourceLink.from_dict(x) for x in resource_links]
    cohort_data_class = CohortData.from_dict(headers=headers, patients=patients)
    
    singleton_json = create_singular_resource(
        singleton_resource_name, resource_definitions_class, resource_links_class, cohort_data_class, 0
    )
    # 1. Top-Level Key Checks
    assert isinstance(singleton_json, dict), "Encounter data must be a dictionary."
    assert singleton_json.get('resourceType') == 'Encounter', "Resource type must be 'Encounter'."
    assert 'id' in singleton_json, "Encounter must have an 'id'."

    # 2. Status and Identifier Checks
    assert singleton_json.get('status') == 'finished', "Encounter status must be 'finished'."
    assert isinstance(singleton_json.get('identifier'), list) and len(singleton_json['identifier']) > 0, \
        "Encounter must have at least one identifier."
    assert singleton_json['identifier'][0].get('value') == '3456', "Identifier value check failed."

    # 3. Class and Type Checks
    encounter_class = singleton_json.get('class', {})
    assert encounter_class.get('code') == 'IMP', "Encounter class code must be 'IMP' (Inpatient)."
    assert singleton_json.get('type', [{}])[0].get('coding', [{}])[0].get('code') == 'O80', \
        "Type coding code must be 'O80'."

    # 4. Period (Datetime) Checks
    encounter_period = singleton_json.get('period', {})
    assert 'start' in encounter_period and 'end' in encounter_period, \
        "Encounter period must have 'start' and 'end' dates."
    assert isinstance(encounter_period['start'], datetime.datetime), \
        "Period 'start' must be a datetime.datetime object."
    assert isinstance(encounter_period['end'], datetime.datetime), \
        "Period 'end' must be a datetime.datetime object."
    assert encounter_period['end'] > encounter_period['start'], \
        "Period 'end' must be after 'start'."

    # 5. Nested Reference Checks
    assert singleton_json.get('subject', {}).get('reference') == 'Patient/PrimaryPatient', \
        "Subject reference check failed."
    assert singleton_json.get('hospitalization', {}).get('dischargeDisposition', {}).get('coding', [{}])[0].get('code') == 'home', \
        "Discharge disposition code must be 'home'."

    # 6. Meta/Profile Check (ensuring US Core compliance is declared)
    assert 'meta' in singleton_json and isinstance(singleton_json['meta'].get('profile'), list) and \
        'http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter' in singleton_json['meta']['profile'], \
        "FHIR US Core profile is missing from meta.profile."

def test_API_creation_10302025():
    resource_definitions = [{'entity_name': 'PrimaryPatient', 'resource_type': 'Patient', 'profiles': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient']}, {'entity_name': 'PrimaryCondition', 'resource_type': 'Condition', 'profiles': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition']}]
    resource_links = [{'origin_resource': 'PrimaryCondition', 'reference_path': 'subject', 'destination_resource': 'PrimaryPatient'}]
    headers = [{'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.name', 'jsonPath': 'Patient.name', 'valueType': 'HumanName', 'valueSets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.birthDate', 'jsonPath': 'Patient.birthDate', 'valueType': 'date', 'valueSets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.gender', 'jsonPath': 'Patient.gender', 'valueType': 'code', 'valueSets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.identifier', 'jsonPath': 'Patient.identifier', 'valueType': 'Identifier', 'valueSets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.active', 'jsonPath': 'Patient.active', 'valueType': 'code', 'valueSets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.address', 'jsonPath': 'Patient.address', 'valueType': 'Address', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.identifier', 'jsonPath': 'Condition.identifier', 'valueType': 'Identifier', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.clinicalStatus', 'jsonPath': 'Condition.clinicalStatus', 'valueType': 'CodeableConcept', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.verificationStatus', 'jsonPath': 'Condition.verificationStatus', 'valueType': 'CodeableConcept', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.category', 'jsonPath': 'Condition.category', 'valueType': 'CodeableConcept', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.code', 'jsonPath': 'Condition.code', 'valueType': '$special', 'valueSets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.onsetDateTime', 'jsonPath': 'Condition.onsetDateTime', 'valueType': 'dateTime', 'valueSets': None}]

    patients = [{('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Male'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Male'}]
    resource_definitions_class: List[ResourceDefinition] = [ResourceDefinition.from_dict(x) for x in resource_definitions]
    resource_links_class = [ResourceLink.from_dict(x) for x in resource_links]
    cohort_data_class = CohortData.from_dict(headers=headers, patients=patients)
    
    fhir_bundle = conversion.create_transaction_bundle(resource_definitions_class, resource_links_class, cohort_data_class, 0)
    # 1. Top-Level Key Checks
    assert isinstance(fhir_bundle, dict)
    primaryPatient = [entry["resource"] for entry in fhir_bundle["entry"] if entry["resource"]["resourceType"] == 'Patient'][0]
    assert primaryPatient
    assert primaryPatient["gender"] == 'Male'
    
def test_API_creation_11032025():
    resource_definitions = [{'entity_name': 'PrimaryPatient', 'resource_type': 'Patient', 'profiles': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient']}, {'entity_name': 'PrimaryCondition', 'resource_type': 'Condition', 'profiles': ['http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition']}]
    resource_links = [{'origin_resource': 'PrimaryCondition', 'reference_path': 'subject', 'destination_resource': 'PrimaryPatient'}]
    headers = [{'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.name', 'jsonpath': 'Patient.name', 'value_type': 'HumanName', 'valuesets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.birthDate', 'jsonpath': 'Patient.birthDate', 'value_type': 'date', 'valuesets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.gender', 'jsonpath': 'Patient.gender', 'value_type': 'code', 'valuesets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.identifier', 'jsonpath': 'Patient.identifier', 'value_type': 'Identifier', 'valuesets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.active', 'jsonpath': 'Patient.active', 'value_type': 'code', 'valuesets': None}, {'entityName': 'PrimaryPatient', 'fieldName': 'PrimaryPatient/Patient.address', 'jsonpath': 'Patient.address', 'value_type': 'Address', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.identifier', 'jsonpath': 'Condition.identifier', 'value_type': 'Identifier', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.clinicalStatus', 'jsonpath': 'Condition.clinicalStatus', 'value_type': 'CodeableConcept', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.verificationStatus', 'jsonpath': 'Condition.verificationStatus', 'value_type': 'CodeableConcept', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.category', 'jsonpath': 'Condition.category', 'value_type': 'CodeableConcept', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.code', 'jsonpath': 'Condition.code', 'value_type': '$special', 'valuesets': None}, {'entityName': 'PrimaryCondition', 'fieldName': 'PrimaryCondition/Condition.onsetDateTime', 'jsonpath': 'Condition.onsetDateTime', 'value_type': 'dateTime', 'valuesets': None}]

    patients = [{('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Male'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Female'}, {('PrimaryPatient', 'PrimaryPatient/Patient.gender'): 'Male'}]
    resource_definitions_class: List[ResourceDefinition] = [ResourceDefinition.from_dict(x) for x in resource_definitions]
    resource_links_class = [ResourceLink.from_dict(x) for x in resource_links]
    cohort_data_class = CohortData.from_dict(headers=headers, patients=patients)
    
    fhir_bundle = conversion.create_transaction_bundle(resource_definitions_class, resource_links_class, cohort_data_class, 0)
    # 1. Top-Level Key Checks
    assert isinstance(fhir_bundle, dict)
    primaryPatient = [entry["resource"] for entry in fhir_bundle["entry"] if entry["resource"]["resourceType"] == 'Patient'][0]
    assert primaryPatient
    assert primaryPatient["gender"] == 'Male'