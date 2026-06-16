import pytest
from src.fhir_sheets.core.conversion import create_resource_link
from src.fhir_sheets.core.model.resource_link_entity import ResourceLink
from src.fhir_sheets.core.config.FhirSheetsConfiguration import FhirSheetsConfiguration


class TestNestedReferencePaths:
    """Test suite for nested reference path handling in create_resource_link"""

    def test_simple_reference_path(self):
        """Test existing behavior with simple reference path like 'subject'"""
        created_resources = {
            'Patient1': {'resourceType': 'Patient', 'id': 'patient-123'},
            'Observation1': {'resourceType': 'Observation', 'id': 'obs-456'}
        }
        link = ResourceLink('Observation1', 'subject', 'Patient1')
        config = FhirSheetsConfiguration({})
        
        create_resource_link(created_resources, link, config)
        
        assert 'subject' in created_resources['Observation1']
        assert created_resources['Observation1']['subject']['reference'] == 'Patient/patient-123'

    def test_nested_path_with_array_index(self):
        """Test nested reference path like 'performer.[0].actor'"""
        created_resources = {
            'Practitioner1': {'resourceType': 'Practitioner', 'id': 'prac-789'},
            'Observation2': {'resourceType': 'Observation', 'id': 'obs-999'}
        }
        link = ResourceLink('Observation2', 'performer.[0].actor', 'Practitioner1')
        config = FhirSheetsConfiguration({})
        
        create_resource_link(created_resources, link, config)
        
        assert 'performer' in created_resources['Observation2']
        assert isinstance(created_resources['Observation2']['performer'], list)
        assert len(created_resources['Observation2']['performer']) >= 1
        assert 'actor' in created_resources['Observation2']['performer'][0]
        assert created_resources['Observation2']['performer'][0]['actor']['reference'] == 'Practitioner/prac-789'

    def test_nested_path_multiple_levels(self):
        """Test nested reference path with multiple levels like 'entry.[0].resource.subject'"""
        created_resources = {
            'Patient2': {'resourceType': 'Patient', 'id': 'patient-abc'},
            'Bundle1': {'resourceType': 'Bundle', 'id': 'bundle-def'}
        }
        link = ResourceLink('Bundle1', 'entry.[0].resource.subject', 'Patient2')
        config = FhirSheetsConfiguration({})
        
        create_resource_link(created_resources, link, config)
        
        assert 'entry' in created_resources['Bundle1']
        assert isinstance(created_resources['Bundle1']['entry'], list)
        assert len(created_resources['Bundle1']['entry']) >= 1
        assert 'resource' in created_resources['Bundle1']['entry'][0]
        assert 'subject' in created_resources['Bundle1']['entry'][0]['resource']
        assert created_resources['Bundle1']['entry'][0]['resource']['subject']['reference'] == 'Patient/patient-abc'

    def test_array_type_reference_simple(self):
        """Test array type reference with simple path (existing behavior)"""
        created_resources = {
            'Practitioner2': {'resourceType': 'Practitioner', 'id': 'prac-111'},
            'Observation3': {'resourceType': 'Observation', 'id': 'obs-222'}
        }
        config = FhirSheetsConfiguration({
            'array_type_references': [('observation', 'practitioner', 'performer')]
        })
        link = ResourceLink('Observation3', 'performer', 'Practitioner2')
        
        create_resource_link(created_resources, link, config)
        
        assert 'performer' in created_resources['Observation3']
        assert isinstance(created_resources['Observation3']['performer'], list)
        assert len(created_resources['Observation3']['performer']) == 1
        assert created_resources['Observation3']['performer'][0]['reference'] == 'Practitioner/prac-111'

    def test_array_type_reference_multiple_additions(self):
        """Test that array type references append correctly"""
        created_resources = {
            'Practitioner3': {'resourceType': 'Practitioner', 'id': 'prac-333'},
            'Practitioner4': {'resourceType': 'Practitioner', 'id': 'prac-444'},
            'Observation4': {'resourceType': 'Observation', 'id': 'obs-555'}
        }
        config = FhirSheetsConfiguration({
            'array_type_references': [('observation', 'practitioner', 'performer')]
        })
        
        link1 = ResourceLink('Observation4', 'performer', 'Practitioner3')
        create_resource_link(created_resources, link1, config)
        
        link2 = ResourceLink('Observation4', 'performer', 'Practitioner4')
        create_resource_link(created_resources, link2, config)
        
        assert 'performer' in created_resources['Observation4']
        assert isinstance(created_resources['Observation4']['performer'], list)
        assert len(created_resources['Observation4']['performer']) == 2
        assert created_resources['Observation4']['performer'][0]['reference'] == 'Practitioner/prac-333'
        assert created_resources['Observation4']['performer'][1]['reference'] == 'Practitioner/prac-444'

    def test_nested_path_with_higher_array_index(self):
        """Test nested path with array index [2] to ensure proper array extension"""
        created_resources = {
            'Organization1': {'resourceType': 'Organization', 'id': 'org-666'},
            'Patient3': {'resourceType': 'Patient', 'id': 'patient-777'}
        }
        link = ResourceLink('Patient3', 'contact.[2].organization', 'Organization1')
        config = FhirSheetsConfiguration({})
        
        create_resource_link(created_resources, link, config)
        
        assert 'contact' in created_resources['Patient3']
        assert isinstance(created_resources['Patient3']['contact'], list)
        assert len(created_resources['Patient3']['contact']) >= 3
        assert 'organization' in created_resources['Patient3']['contact'][2]
        assert created_resources['Patient3']['contact'][2]['organization']['reference'] == 'Organization/org-666'

    def test_preview_mode_reference_value(self):
        """Test that preview mode uses entity name instead of resource id"""
        created_resources = {
            'Patient4': {'resourceType': 'Patient', 'id': 'patient-888'},
            'Observation5': {'resourceType': 'Observation', 'id': 'obs-999'}
        }
        config = FhirSheetsConfiguration({'preview_mode': True})
        link = ResourceLink('Observation5', 'subject', 'Patient4')
        
        create_resource_link(created_resources, link, config)
        
        assert created_resources['Observation5']['subject']['reference'] == 'Patient/Patient4'

    def test_nested_path_preview_mode(self):
        """Test nested path in preview mode"""
        created_resources = {
            'Practitioner5': {'resourceType': 'Practitioner', 'id': 'prac-aaa'},
            'Observation6': {'resourceType': 'Observation', 'id': 'obs-bbb'}
        }
        config = FhirSheetsConfiguration({'preview_mode': True})
        link = ResourceLink('Observation6', 'performer.[0].actor', 'Practitioner5')
        
        create_resource_link(created_resources, link, config)
        
        assert created_resources['Observation6']['performer'][0]['actor']['reference'] == 'Practitioner/Practitioner5'

    def test_missing_origin_resource(self):
        """Test that missing origin resource is handled gracefully"""
        created_resources = {
            'Patient5': {'resourceType': 'Patient', 'id': 'patient-ccc'}
        }
        config = FhirSheetsConfiguration({})
        link = ResourceLink('NonExistentObservation', 'subject', 'Patient5')
        
        # Should not raise an exception, just log a warning
        create_resource_link(created_resources, link, config)
        
        # Origin resource doesn't exist, so nothing should be modified
        assert 'NonExistentObservation' not in created_resources

    def test_missing_destination_resource(self):
        """Test that missing destination resource is handled gracefully"""
        created_resources = {
            'Observation7': {'resourceType': 'Observation', 'id': 'obs-ddd'}
        }
        config = FhirSheetsConfiguration({})
        link = ResourceLink('Observation7', 'subject', 'NonExistentPatient')
        
        # Should not raise an exception, just log a warning
        create_resource_link(created_resources, link, config)
        
        # Destination doesn't exist, so reference shouldn't be created
        assert 'subject' not in created_resources['Observation7']