import datetime
import pathlib
import json
from typing import Iterable, Dict
from src.fhir_sheets.core.conversion import create_singular_resource
from src.fhir_sheets.core.model.cohort_data_entity import CohortData
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition
from src.fhir_sheets.core.model.resource_link_entity import ResourceLink
from src.fhir_sheets.cli.main import main

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


def test_singleton_resource_creationg():
    resource_definitions = [
        {
            "Entity Name": "PrimaryEncounter",
            "ResourceType": "Encounter",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"
            ],
            None: None,
        },
        {
            "Entity Name": "PrimaryPatient",
            "ResourceType": "Patient",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
            ],
            None: None,
        },
        {
            "Entity Name": "Mother",
            "ResourceType": "RelatedPerson",
            "Profile(s)": None,
            None: None,
        },
        {
            "Entity Name": "HearingScreening",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            None: None,
        },
        {
            "Entity Name": "CMVTest",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            None: None,
        },
        {
            "Entity Name": "Ultrasound",
            "ResourceType": "Procedure",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
            ],
            None: None,
        },
        {
            "Entity Name": "Diagnosis",
            "ResourceType": "Condition",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"
            ],
            None: None,
        },
        {
            "Entity Name": "Valganciclovir",
            "ResourceType": "MedicationRequest",
            "Profile(s)": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"
            ],
            None: None,
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
            "jsonpath": "Patient.extension[Race].ombCategory",
            "valueType": None,
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-omb-race-category.html",
        },
        {
            "fieldName": "Patient's OMB Ethnicity Category",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.extension[Ethnicity].ombCategory.value",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-omb-ethnicity-category.html",
        },
        {
            "fieldName": "Patient's Sex at Birth",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.extension[Birthsex].value",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-birthsex.html",
        },
        {
            "fieldName": "Patient Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier.[0].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient Identifier System",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier.[0].system",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient MRN Identifier System",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier[type=MRN].system",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient MRN Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier[type=MRN].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient SSN Identifier System",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier[type=SSN].system",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient SSN Identifier Value",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.identifier[type=SSN].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Given Name",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.name.[0].given",
            "valueType": "string[]",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Family Name",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.name.[0].family",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient name Use (Type)",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.name[0].use",
            "valueType": "code",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Telecom System (Type)",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.telecom.[0].system",
            "valueType": "string",
            "valuesets": "https://hl7.org/fhir/R4/valueset-contact-point-system.html",
        },
        {
            "fieldName": "Patient's Telecom Number",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.telecom.[0].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Telecom Purpose",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.telecom.[0].use",
            "valueType": "string",
            "valuesets": "https://hl7.org/fhir/R4/valueset-contact-point-use.html",
        },
        {
            "fieldName": "Patient's Gender",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.gender",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-administrative-gender.html",
        },
        {
            "fieldName": "Patient's Date of Birth",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.birthDate",
            "valueType": "date",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Primary Address",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.address.[0]",
            "valueType": "Address",
            "valuesets": None,
        },
        {
            "fieldName": "Patient's Communication Language",
            "entityName": "PrimaryPatient",
            "jsonpath": "Patient.communication.[0].language",
            "valueType": "CodeableConcept",
            "valuesets": None,
        },
        {
            "fieldName": "Encounter identifier namespace",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.identifier.[0].system",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Encounter Identifier",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.identifier.[0].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Encounter Status",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.status",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-encounter-status.html",
        },
        {
            "fieldName": "Encounter patient classification",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.class",
            "valueType": "Coding",
            "valuesets": "https://hl7.org/fhir/R4/v3/ActEncounterCode/vs.html",
        },
        {
            "fieldName": "Specific Encounter Type",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.type.[0]",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-encounter-type.html",
        },
        {
            "fieldName": "Encounter Start Date",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.period.start",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Encounter End Date",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.period.end",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Type of Facility Patient Discharged To",
            "entityName": "PrimaryEncounter",
            "jsonpath": "Encounter.hospitalization.dischargeDisposition",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/R4/valueset-encounter-discharge-disposition.html",
        },
        {
            "fieldName": "Mother identifier namespace",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.identifier.[0].system",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Mother identifier",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.identifier.[0].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Mother Relationship Code",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.relationship.[0]",
            "valueType": "CodeableConcept",
            "valuesets": "https://www.hl7.org/fhir/r4/valueset-relatedperson-relationshiptype.html",
        },
        {
            "fieldName": "Mother's Given Name",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.name.[0].given",
            "valueType": "string[]",
            "valuesets": None,
        },
        {
            "fieldName": "Mother's Family Name",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.name.[0].family",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Mother's name Use (Type)",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.name[0].use",
            "valueType": "code",
            "valuesets": None,
        },
        {
            "fieldName": "Mother's Telecom System (Type)",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.telecom.[0].system",
            "valueType": "string",
            "valuesets": "https://hl7.org/fhir/R4/valueset-contact-point-system.html",
        },
        {
            "fieldName": "Mother's Telecom Number",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.telecom.[0].value",
            "valueType": "string",
            "valuesets": None,
        },
        {
            "fieldName": "Mother's Telecom Purpose",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.telecom.[0].use",
            "valueType": "string",
            "valuesets": "https://hl7.org/fhir/R4/valueset-contact-point-use.html",
        },
        {
            "fieldName": "Mother's Gender",
            "entityName": "Mother",
            "jsonpath": "RelatedPerson.gender",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-administrative-gender.html",
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "HearingScreening",
            "jsonpath": "Procedure.status",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "HearingScreening",
            "jsonpath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "HearingScreening",
            "jsonpath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "CMVTest",
            "jsonpath": "Procedure.status",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "CMVTest",
            "jsonpath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "CMVTest",
            "jsonpath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Procedure Event Status",
            "entityName": "Ultrasound",
            "jsonpath": "Procedure.status",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-event-status.html",
        },
        {
            "fieldName": "Procedure code",
            "entityName": "Ultrasound",
            "jsonpath": "Procedure.code",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-procedure-code.html",
        },
        {
            "fieldName": "Procedure's Performed Datetime",
            "entityName": "Ultrasound",
            "jsonpath": "Procedure.performedDateTime",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Condition Clinical Status",
            "entityName": "Diagnosis",
            "jsonpath": "Condition.clinicalStatus",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/R4/valueset-condition-clinical.html",
        },
        {
            "fieldName": "Condition Verification Status",
            "entityName": "Diagnosis",
            "jsonpath": "Condition.verificationStatus",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/R4/valueset-condition-ver-status.html",
        },
        {
            "fieldName": "Condition Category",
            "entityName": "Diagnosis",
            "jsonpath": "Condition.category.[0]",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-condition-category.html",
        },
        {
            "fieldName": "Condition Code",
            "entityName": "Diagnosis",
            "jsonpath": "Condition.code",
            "valueType": "CodeableConcept",
            "valuesets": None,
        },
        {
            "fieldName": "Condition Onset Date",
            "entityName": "Diagnosis",
            "jsonpath": "Condition.onsetDateTime",
            "valueType": "datetime",
            "valuesets": None,
        },
        {
            "fieldName": "Medication Request Status",
            "entityName": "Valganciclovir",
            "jsonpath": "MedicationRequest.status",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-medicationrequest-status.html",
        },
        {
            "fieldName": "Medication Request Intent",
            "entityName": "Valganciclovir",
            "jsonpath": "MedicationRequest.intent",
            "valueType": "code",
            "valuesets": "https://hl7.org/fhir/R4/valueset-medicationrequest-intent.html",
        },
        {
            "fieldName": "Medication Code",
            "entityName": "Valganciclovir",
            "jsonpath": "MedicationRequest.medicationCodeableConcept",
            "valueType": "CodeableConcept",
            "valuesets": "https://hl7.org/fhir/us/core/STU3.1.1/ValueSet-us-core-medication-codes.html",
        },
        {
            "fieldName": "Medication Date",
            "entityName": "Valganciclovir",
            "jsonpath": "MedicationRequest.authoredOn",
            "valueType": "dateTime",
            "valuesets": None,
        },
        {
            "fieldName": "Medication Dosage Instructions",
            "entityName": "Valganciclovir",
            "jsonpath": "MedicationRequest.dosageInstruction.[0].text",
            "valueType": "string",
            "valuesets": None,
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
    resource_definitions_class = [ResourceDefinition(x) for x in resource_definitions]
    resource_links_class = [ResourceLink(x) for x in resource_links]
    cohort_data_class = CohortData(headers=headers, patients=patients)
    
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
