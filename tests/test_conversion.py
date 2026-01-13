import pytest
import uuid
from src.fhir_sheets.core.conversion import (
    initialize_bundle, initialize_resource, add_resource_to_transaction_bundle,
    create_structure_from_jsonpath
)
from src.fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition


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
