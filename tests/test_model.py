import pytest
from src.fhir_sheets.core.model.cohort_data_entity import CohortData, HeaderEntry, PatientEntry
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition
from src.fhir_sheets.core.model.resource_link_entity import ResourceLink
from src.fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration


class TestCohortData:
    def test_from_dict_valid(self):
        headers = [
            {"entityName": "Patient", "fieldName": "name", "jsonPath": "Patient.name", "valueType": "string", "valueSets": None},
            {"entityName": "Patient", "fieldName": "birthDate", "jsonPath": "Patient.birthDate", "valueType": "date", "valueSets": None}
        ]
        patients = [
            {("Patient", "name"): "John Doe", ("Patient", "birthDate"): "1990-01-01"},
            {("Patient", "name"): "Jane Smith", ("Patient", "birthDate"): "1985-05-15"}
        ]
        cohort = CohortData.from_dict(headers, patients)
        assert cohort.get_num_patients() == 2
        assert len(cohort.headers) == 2
        assert len(cohort.patients) == 2

    def test_from_dict_empty(self):
        cohort = CohortData.from_dict([], [])
        assert cohort.get_num_patients() == 0

    def test_get_num_patients(self):
        headers = [{"entityName": "Patient", "fieldName": "name", "jsonPath": "Patient.name", "valueType": "string", "valueSets": None}]
        patients = [
            {("Patient", "name"): "Patient1"},
            {("Patient", "name"): "Patient2"},
            {("Patient", "name"): "Patient3"}
        ]
        cohort = CohortData.from_dict(headers, patients)
        assert cohort.get_num_patients() == 3


class TestHeaderEntry:
    def test_from_dict(self):
        data = {
            "entityName": "Patient",
            "fieldName": "Patient.name",
            "jsonPath": "Patient.name",
            "valueType": "HumanName",
            "valueSets": None
        }
        header = HeaderEntry.from_dict(data)
        assert header.entityName == "Patient"
        assert header.fieldName == "Patient.name"
        assert header.jsonPath == "Patient.name"
        assert header.valueType == "HumanName"
        assert header.valueSets is None


class TestPatientEntry:
    def test_from_dict(self):
        entries = {
            ("Patient", "name"): "John Doe",
            ("Patient", "birthDate"): "1990-01-01"
        }
        patient = PatientEntry.from_dict(entries)
        assert patient.entries == entries

    def test_repr(self):
        entries = {("Patient", "name"): "Test"}
        patient = PatientEntry(entries)
        assert "PatientEntry" in repr(patient)


class TestResourceDefinition:
    def test_from_dict(self):
        data = {
            "entity_name": "PrimaryPatient",
            "resource_type": "Patient",
            "profiles": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        }
        rd = ResourceDefinition.from_dict(data)
        assert rd.entityName == "PrimaryPatient"
        assert rd.resourceType == "Patient"
        assert rd.profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]

    def test_from_dict_alternate_keys(self):
        # Test with different key casing as seen in some tests
        data = {
            "Entity Name": "PrimaryEncounter",
            "ResourceType": "Encounter",
            "Profile(s)": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"]
        }
        rd = ResourceDefinition.from_dict(data)
        assert rd.entityName == "PrimaryEncounter"
        assert rd.resourceType == "Encounter"
        assert rd.profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"]

    def test_repr(self):
        rd = ResourceDefinition("Patient", "Patient", [])
        assert "ResourceDefinition" in repr(rd)


class TestResourceLink:
    def test_from_dict(self):
        data = {
            "origin_resource": "Encounter",
            "reference_path": "subject",
            "destination_resource": "Patient"
        }
        rl = ResourceLink.from_dict(data)
        assert rl.originResource == "Encounter"
        assert rl.referencePath == "subject"
        assert rl.destinationResource == "Patient"

    def test_from_dict_alternate_keys(self):
        data = {
            "OriginResource": "Procedure",
            "ReferencePath": "subject",
            "DestinationResource": "Patient"
        }
        rl = ResourceLink.from_dict(data)
        assert rl.originResource == "Procedure"
        assert rl.referencePath == "subject"
        assert rl.destinationResource == "Patient"

    def test_repr(self):
        rl = ResourceLink("A", "ref", "B")
        assert "ResourceLink" in repr(rl)


class TestFhirSheetsConfiguration:
    def test_init_empty(self):
        config = FhirSheetsConfiguration({})
        assert config.preview_mode == False
        assert config.medications_as_reference == False
        assert isinstance(config.random_seed, int)

    def test_init_with_data(self):
        data = {"preview_mode": True, "medications_as_reference": True, "random_seed": 12345}
        config = FhirSheetsConfiguration(data)
        assert config.preview_mode == True
        assert config.medications_as_reference == True
        assert config.random_seed == 12345

    def test_repr(self):
        config = FhirSheetsConfiguration({"preview_mode": True})
        assert "FhirSheetsConfiguration" in repr(config)
        assert "preview_mode=True" in repr(config)
