import pytest
from src.fhir_sheets.core.special_values import (
    DataAbsentReasonHandler, PatientRaceExtensionValueHandler,
    PatientEthnicityExtensionValueHandler, PatientBirthSexExtensionValueHandler,
    PatientMRNIdentifierValueHandler, PatientSSNIdentifierValueHandler,
    utilFindExtensionWithURL, findComponentWithCoding
)
from src.fhir_sheets.core.model.resource_definition_entity import ResourceDefinition


class TestDataAbsentReasonHandler:
    def test_assign_value_masked(self):
        handler = DataAbsentReasonHandler()
        final_struct = {}
        handler.assign_value(final_struct, "name", "$masked", "string")
        assert 'extension' in final_struct
        assert len(final_struct['extension']) == 1
        ext = final_struct['extension'][0]
        assert ext['url'] == 'http://hl7.org/fhir/StructureDefinition/data-absent-reason'
        assert ext['value'] == 'masked'

    def test_assign_value_unknown(self):
        handler = DataAbsentReasonHandler()
        final_struct = {}
        handler.assign_value(final_struct, "birthDate", "$unknown", "date")
        assert 'extension' in final_struct
        ext = final_struct['extension'][0]
        assert ext['value'] == 'unknown'

    def test_assign_value_on_list(self):
        handler = DataAbsentReasonHandler()
        final_struct = []
        handler.assign_value(final_struct, "name", "$masked", "string")
        assert len(final_struct) == 1
        assert 'extension' in final_struct[0]
        ext = final_struct[0]['extension'][0]
        assert ext['value'] == 'masked'


class TestPatientRaceExtensionValueHandler:
    def test_assign_value_asian(self):
        handler = PatientRaceExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.extension[Race].ombCategory", rd, "string", final_struct, "ombCategory", "Asian")
        assert 'extension' in final_struct
        race_ext = None
        for ext in final_struct['extension']:
            if ext.get('url') == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race':
                race_ext = ext
                break
        assert race_ext is not None
        assert len(race_ext['extension']) == 2
        omb_ext = race_ext['extension'][0]
        assert omb_ext['url'] == 'ombCategory'
        assert omb_ext['valueCoding']['code'] == '2028-9'
        text_ext = race_ext['extension'][1]
        assert text_ext['valueString'] == 'asian'

    def test_assign_value_white(self):
        handler = PatientRaceExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.extension[Race].ombCategory", rd, "string", final_struct, "ombCategory", "White")
        race_ext = final_struct['extension'][0]
        omb_ext = race_ext['extension'][0]
        assert omb_ext['valueCoding']['code'] == '2106-3'

    def test_assign_value_no_match(self):
        """When the race value does not match any known category the handler should return an empty dict."""
        handler = PatientRaceExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        result = handler.assign_value(
            "Patient.extension[Race].ombCategory",
            rd,
            "string",
            final_struct,
            "ombCategory",
            "nonexistentrace",
        )
        assert result == {}
        # final_struct should remain empty because no extension was added
        assert final_struct == {}


class TestPatientEthnicityExtensionValueHandler:
    def test_assign_value_hispanic(self):
        handler = PatientEthnicityExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.extension[Ethnicity].ombCategory", rd, "string", final_struct, "ombCategory", "Hispanic or Latino")
        assert 'extension' in final_struct
        ethnicity_ext = final_struct['extension'][0]
        assert ethnicity_ext['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'
        omb_ext = ethnicity_ext['extension'][0]
        assert omb_ext['valueCoding']['code'] == '2135-2'

    def test_assign_value_not_hispanic(self):
        """Verify that the handler correctly processes the "Not Hispanic or Latino"
        ethnicity category (key "Non Hispanic or Latino"). The resulting extension
        should contain the appropriate coding with code '2186-5' and the text value
        should match the key used in the handler.
        """
        handler = PatientEthnicityExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        # Use the exact key as defined in the handler's omb_categories
        handler.assign_value(
            "Patient.extension[Ethnicity].ombCategory",
            rd,
            "string",
            final_struct,
            "ombCategory",
            "Not Hispanic or Latino",
        )
        assert 'extension' in final_struct
        ethnicity_ext = final_struct['extension'][0]
        assert ethnicity_ext['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'
        omb_ext = ethnicity_ext['extension'][0]
        # Verify the correct code for "Not Hispanic or Latino"
        assert omb_ext['valueCoding']['code'] == '2186-5'
        # The valueString should be set to the key (preserving case)
        text_ext = ethnicity_ext['extension'][1]
        assert text_ext['valueString'] == 'Not Hispanic or Latino'

    def test_assign_value_no_match(self):
        """When the ethnicity value does not match any known category the handler should return an empty dict."""
        handler = PatientEthnicityExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        result = handler.assign_value(
            "Patient.extension[Ethnicity].ombCategory",
            rd,
            "string",
            final_struct,
            "ombCategory",
            "nonexistentethnicity",
        )
        assert result == {}
        assert final_struct == {}


class TestPatientBirthSexExtensionValueHandler:
    def test_assign_value_male(self):
        handler = PatientBirthSexExtensionValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.extension[Birthsex].value", rd, "code", final_struct, "value", "M")
        assert 'extension' in final_struct
        birthsex_ext = final_struct['extension'][0]
        assert birthsex_ext['url'] == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex'
        assert birthsex_ext['valueCode'] == 'M'


class TestPatientMRNIdentifierValueHandler:
    def test_assign_system(self):
        handler = PatientMRNIdentifierValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.identifier[type=MR].system", rd, "string", final_struct, "system", "urn:mrn:test")
        assert 'identifier' in final_struct
        assert len(final_struct['identifier']) == 1
        ident = final_struct['identifier'][0]
        assert ident['type']['coding'][0]['code'] == 'MR'
        assert ident['system'] == 'urn:mrn:test'

    def test_assign_value(self):
        handler = PatientMRNIdentifierValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.identifier[type=MR].value", rd, "string", final_struct, "value", "12345")
        ident = final_struct['identifier'][0]
        assert ident['value'] == '12345'


class TestPatientSSNIdentifierValueHandler:
    def test_assign_value(self):
        handler = PatientSSNIdentifierValueHandler()
        rd = ResourceDefinition("Patient", "Patient", [])
        final_struct = {}
        handler.assign_value("Patient.identifier[type=SSN].value", rd, "string", final_struct, "value", "123-45-6789")
        assert 'identifier' in final_struct
        ident = final_struct['identifier'][0]
        assert ident['type']['coding'][0]['code'] == 'SS'
        assert ident['value'] == '123-45-6789'


class TestUtilFindExtensionWithURL:
    def test_find_existing_extension(self):
        extension_block = [
            {"url": "http://example.com/ext1", "value": "test1"},
            {"url": "http://example.com/ext2", "value": "test2"}
        ]
        result = utilFindExtensionWithURL(extension_block, "http://example.com/ext2")
        assert result == extension_block[1]

    def test_find_nonexistent_extension(self):
        extension_block = [
            {"url": "http://example.com/ext1", "value": "test1"}
        ]
        result = utilFindExtensionWithURL(extension_block, "http://example.com/ext3")
        assert result is None


class TestFindComponentWithCoding:
    def test_find_existing_component(self):
        components = [
            {
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "1234-5"}
                    ]
                }
            },
            {
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "5678-9"}
                    ]
                }
            }
        ]
        result = findComponentWithCoding(components, "5678-9")
        assert result == components[1]

    def test_find_nonexistent_component(self):
        components = [
            {
                "code": {
                    "coding": [
                        {"system": "http://loinc.org", "code": "1234-5"}
                    ]
                }
            }
        ]
        result = findComponentWithCoding(components, "9999-9")
        assert result is None
