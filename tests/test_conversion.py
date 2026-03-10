import pytest
import uuid
from src.fhir_sheets.core.conversion import (
    initialize_bundle, initialize_resource, add_resource_to_transaction_bundle,
    create_structure_from_jsonpath
)
from src.fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition

import json
from src.fhir_sheets.core.conversion import clean_empty


class TestInitializeBundle:
    def test_initialize_bundle_default(self):
        config = FhirSheetsConfiguration({})
        bundle = initialize_bundle(config)
        assert bundle['resourceType'] == 'Bundle'
        assert bundle['type'] == 'transaction'
        assert 'id' in bundle
        assert 'meta' in bundle
        assert 'entry' in bundle
        assert bundle['entry'] == []
        assert isinstance(bundle['id'], str)

    def test_initialize_bundle_with_config(self):
        config = FhirSheetsConfiguration({"preview_mode": True})
        bundle = initialize_bundle(config)
        assert bundle['resourceType'] == 'Bundle'
        assert bundle['type'] == 'transaction'
        
    def test_initialize_bundle_distinct_ids(self):
        config = FhirSheetsConfiguration({"preview_mode": True})
        bundleA = initialize_bundle(config)
        bundleB = initialize_bundle(config)
        bundleA_id = bundleA['id']
        bundleB_id = bundleB['id']
        assert bundleA_id != bundleB_id


class TestInitializeResource:
    def test_initialize_resource_basic(self):
        rd = ResourceDefinition("Patient", "Patient", [])
        resource = initialize_resource(rd)
        assert resource['resourceType'] == 'Patient'
        assert 'id' in resource
        assert 'meta' not in resource  # No profiles

    def test_initialize_resource_with_profiles(self):
        profiles = ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        rd = ResourceDefinition("Patient", "Patient", profiles)
        resource = initialize_resource(rd)
        assert resource['resourceType'] == 'Patient'
        assert 'meta' in resource
        assert 'profile' in resource['meta']
        assert resource['meta']['profile'] == profiles


class TestAddResourceToTransactionBundle:
    def test_add_resource_to_bundle(self):
        config = FhirSheetsConfiguration({})
        bundle = initialize_bundle(config)
        resource = {'resourceType': 'Patient', 'id': 'test-id'}

        result = add_resource_to_transaction_bundle(bundle, resource)
        assert len(result['entry']) == 1
        entry = result['entry'][0]
        assert 'fullUrl' in entry
        assert 'resource' in entry
        assert 'request' in entry
        assert entry['resource'] == resource
        assert entry['fullUrl'] == "urn:uuid:test-id"
        assert entry['request']['method'] == "PUT"
        assert entry['request']['url'] == "Patient/test-id"


class TestCreateStructureFromJsonpath:
    def test_create_structure_nested_path(self):
        root = {}
        rd = ResourceDefinition("Patient", "Patient", [])
        result = create_structure_from_jsonpath(root, "Patient.name.family", rd, "string", "Doe")
        assert result['name']['family'] == "Doe"

    def test_create_structure_array_index(self):
        root = {}
        rd = ResourceDefinition("Patient", "Patient", [])
        result = create_structure_from_jsonpath(root, "Patient.name.[0].family", rd, "string", "Doe")
        assert result['name'][0]['family'] == "Doe"

    def test_create_structure_none_value(self):
        root = {}
        rd = ResourceDefinition("Patient", "Patient", [])
        result = create_structure_from_jsonpath(root, "Patient.name", rd, "string", None)
        # Currently converts None to string "None" due to type conversion order
        assert result == {'name': 'None'}

    def test_create_structure_with_datatype_conversion(self):
        root = {}
        rd = ResourceDefinition("Patient", "Patient", [])
        result = create_structure_from_jsonpath(root, "Patient.active", rd, "string", 123)
        assert result['active'] == "123"  # Converted to string


class TestCleanEmptyFunction:
    def test_clean_empty_removes_empty_structures(self):
        """Ensure that clean_empty removes empty dicts, lists, and None values.

        The provided JSON includes a ``dosageInstruction`` field that contains a
        list with a single empty dictionary. After cleaning, the field should be
        removed entirely from the resulting dictionary.
        """
        json_input = """
        {
            "resourceType": "MedicationRequest",
            "id": "136b3216-dfe4-4509-9565-4f7e769f08c9",
            "meta": {
              "profile": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"
              ],
              "security": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                  "code": "HTEST",
                  "display": "test health data"
                }
              ]
            },
            "status": "active",
            "intent": "plan",
            "medicationCodeableConcept": {
              "coding": [
                {
                  "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                  "code": "2711688",
                  "display": "allantoin 0.0075 MG/MG Medicated Patch"
                }
              ]
            },
            "dosageInstruction": [
              {}
            ],
            "subject": {
              "reference": "Patient/eebf273b-9d52-4fc6-8e26-081fded5a497"
            }
          }
        """
        data = json.loads(json_input)
        cleaned = clean_empty(data)
        # The dosageInstruction key should be removed because it only contained an empty dict.
        assert "dosageInstruction" not in cleaned
        # Verify that other top‑level keys remain unchanged.
        assert cleaned["resourceType"] == "MedicationRequest"
        assert cleaned["status"] == "active"
        # Re‑serialize to ensure the result is JSON‑serializable.
        serialized = json.dumps(cleaned)
        assert isinstance(serialized, str)
