
from . import conversion

from abc import ABC, abstractmethod

# Define an abstract base class
class AbstractCustomValueHandler(ABC):
    
    @abstractmethod
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        pass
    
class PatientRaceExtensionValueHandler(AbstractCustomValueHandler):
    omb_categories = {
      "american indian or alaska native" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "1002-5",
          "display" : "American Indian or Alaska Native"
          }
      },
      "asian" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2028-9",
          "display" : "Asian"
          }
      },
      "black or african american" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2054-5",
          "display" : "Black or African American"
          }
      },
      "native hawaiian or other pacific islander" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2054-5",
          "display" : "Native Hawaiian or Other Pacific Islander"
          }  
      },
      "white" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2106-3",
          "display" : "White"
        }
      }
    }
    
    initial_race_json = {
      "extension" : [
        {
          "$ombCategory"
        },
        {
          "url" : "text",
          "valueString" : "$text"
        }
      ],
      "url" : "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
    }
    #Create an ombcategory and detailed section of race extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the race extension if it exists; make it if it does not.
        if 'extension' not in final_struct:
            final_struct['extension'] = []
        race_block = utilFindExtensionWithURL(final_struct['extension'], 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race')
        if race_block is None:
            race_block = self.initial_race_json
            final_struct['extension'].append(race_block)
        for race_key, race_structure in self.omb_categories.items():
            if value.strip().lower() == race_key:
                # Replace $ombCategory in the extension list
                for i, item in enumerate(race_block["extension"]):
                    if isinstance(item, set) and "$ombCategory" in item:
                        # Replace the set with the new structure
                        race_block["extension"][i] = race_structure
                    elif isinstance(item, dict) and item.get("valueString") == "$text":
                        item['valueString'] = race_key
                return final_struct
        pass

class PatientEthnicityExtensionValueHandler(AbstractCustomValueHandler):
    omb_categories = {
      "Hispanic or Latino" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2135-2",
          "display" : "Hispanic or Latino"
          }
      },
      "Non Hispanic or Latino" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2186-5",
          "display" : "Not Hispanic or Latino"
          }
      },
      "Not Hispanic or Latino" : {
        "url" : "ombCategory",
        "valueCoding" : {
          "system" : "urn:oid:2.16.840.1.113883.6.238",
          "code" : "2186-5",
          "display" : "Not Hispanic or Latino"
          }
      }
    }
    
    initial_ethnicity_json = {
      "extension" : [
        {
          "$ombCategory"
        },
        {
          "url" : "text",
          "valueString" : "$text"
        }
      ],
      "url" : "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
    }
    #Create an ombcategory and detailed section of ethnicitiy extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the ethncitiy extension if it exists; make it if it does not.
        if 'extension' not in final_struct:
            final_struct['extension'] = []
        ethnicity_block = utilFindExtensionWithURL(final_struct['extension'], 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')
        if ethnicity_block is None:
            ethnicity_block = self.initial_ethnicity_json
            final_struct['extension'].append(ethnicity_block)
        for race_key, race_structure in self.omb_categories.items():
            if value.strip().lower() == race_key.strip().lower():
                # Replace $ombCategory in the extension list
                for i, item in enumerate(ethnicity_block["extension"]):
                    if isinstance(item, set) and "$ombCategory" in item:
                        # Replace the set with the new structure
                        ethnicity_block["extension"][i] = race_structure
                    elif isinstance(item, dict) and item.get("valueString") == "$text":
                        item['valueString'] = race_key
                return final_struct
        pass
      
class PatientBirthSexExtensionValueHandler(AbstractCustomValueHandler):
    birth_sex_block = {
      "url" : "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
      "valueCode" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'extension' not in final_struct:
            final_struct['extension'] = []
        birthsex_block = utilFindExtensionWithURL(final_struct['extension'], 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')
        if birthsex_block is None:
            birthsex_block = self.birth_sex_block
            birthsex_block['valueCode'] = value
            final_struct['extension'].append(birthsex_block)
        pass
      
class PatientMRNIdentifierValueHandler(AbstractCustomValueHandler):
    patient_mrn_block = {
      "use" : "usual",
      "type" : {
        "coding" : [
          {
            "system" : "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code" : "MR",
            "display" : "Medical Record Number"
          }
        ],
        "text" : "Medical Record Number"
      },
      "system" : "$system",
      "value" : "$value"
    }
    #Assign a MRN identifier
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the MRN identifier if it exists; make it if it does not.
        target_identifier = self.patient_mrn_block
        new_identifier = True
        if 'identifier' not in final_struct:
          final_struct['identifier'] = []
        for identifier in final_struct['identifier']:
          if 'type' in identifier:
            for coding in identifier['type']['coding']:
              if coding['code'] == 'MR':
                target_identifier = identifier
                new_identifier = False
        if new_identifier:
          final_struct['identifier'].append(target_identifier)
        target_identifier[key] = value
        pass
      
class PatientSSNIdentifierValueHandler(AbstractCustomValueHandler):
    patient_mrn_block = {
      "use" : "usual",
      "type" : {
        "coding" : [
          {
            "system" : "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code" : "SS"
          }
        ],
        "text" : "Social Security Number"
      },
      "system" : "$system",
      "value" : "$value"
    }
    #Assign a MRN identifier
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the MRN identifier if it exists; make it if it does not.
        target_identifier = self.patient_mrn_block
        new_identifier = True
        if 'identifier' not in final_struct:
          final_struct['identifier'] = []
        for identifier in final_struct['identifier']:
          if 'type' in identifier:
            for coding in identifier['type']['coding']:
              if coding['code'] == 'SS':
                target_identifier = identifier
                new_identifier = False
        if new_identifier:
          final_struct['identifier'].append(target_identifier)
        target_identifier[key] = value
        pass
      
class OrganizationIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block = {
      "system" : "http://hl7.org.fhir/sid/us-npi",
      "value" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "http://hl7.org.fhir/sid/us-npi"), None)
        if identifier_block is None:
          identifier_block = self.npi_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = str(value)
        pass
      
class OrganizationIdentiferCLIAValueHandler(AbstractCustomValueHandler):
    clia_identifier_block = {
      "system" : "urn:oid:2.16.840.1.113883.4.7",
      "value" : "$value"
    }
    #Assign a birthsex extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "urn:oid:2.16.840.1.113883.4.7"), None)
        if identifier_block is None:
          identifier_block = self.clia_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = str(value)
        pass
      
class PractitionerIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block = {
      "system" : "http://hl7.org.fhir/sid/us-npi",
      "value" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "http://hl7.org.fhir/sid/us-npi"), None)
        if identifier_block is None:
          identifier_block = self.npi_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = value
        pass
      
class ObservationComponentHandler(AbstractCustomValueHandler):
    pulse_oximetry_oxygen_flow_rate = {
      "code" : {
        "coding" : [
          {
            "system" : "http://loinc.org",
            "code" : "3151-8",
            "display" : "Inhaled oxygen flow rate"
          }
        ],
        "text" : "Inhaled oxygen flow rate"
      }
    }
    pulse_oximetry_oxygen_concentration = {
      "code" : {
        "coding" : [
          {
            "system" : "http://loinc.org",
            "code" : "3150-0",
            "display" : "Inhaled oxygen concentration"
          }
        ],
        "text" : "Inhaled oxygen concentration"
      }
    }
    #Find the appropriate component for the observaiton; then call build_structure again to continue the drill down
    def assign_value(self, json_path, resource_definition, final_struct, key, value):
        #Check to make sure the component part exists
        if 'component' not in final_struct:
          final_struct['component'] = []
        components = final_struct['component']
        #Look through the qualifier parts.
        parts = json_path.split('.')
        key_part = parts[1][:parts[1].index('[')]
        qualifier = parts[1][parts[1].index('[')+1:parts[1].index(']')]
        qualifier_condition = qualifier.split('=')
        
        target_component = None
        if qualifier_condition[0] == 'code' and qualifier_condition[1] == '3151-8':
          target_component = findComponentWithCoding(components, '3151-8') or self.pulse_oximetry_oxygen_flow_rate
          if target_component is self.pulse_oximetry_oxygen_flow_rate:
            components.append(target_component)
        if qualifier_condition[0] == 'code' and qualifier_condition[1] == '3150-0':
          target_component = findComponentWithCoding(components, '3150-0') or self.pulse_oximetry_oxygen_concentration
          if target_component is self.pulse_oximetry_oxygen_concentration:
            components.append(target_component)
        #Recurse back down into 
        return conversion.build_structure(target_component, '.'.join(parts[2:]), resource_definition, parts[2:], value, parts[:2])
        pass

def utilFindExtensionWithURL(extension_block, url):
    for extension in extension_block:
        if "url" in extension and extension['url'] == url:
            return extension
        return None

def findComponentWithCoding(components, code):
  return next((component for component in components if any(coding['code'] == code for coding in component['code']['coding'])), None)

#Data dictionary of jsonpaths to match vs classes that need to be called
custom_handlers = {
    "Patient.extension[Race].ombCategory": PatientRaceExtensionValueHandler(),
    "Patient.extension[Ethnicity].ombCategory": PatientEthnicityExtensionValueHandler(),
    "Patient.extension[Birthsex].value": PatientBirthSexExtensionValueHandler(),
    "Patient.identifier[type=MR].system": PatientMRNIdentifierValueHandler(),
    "Patient.identifier[type=MR].value": PatientMRNIdentifierValueHandler(),
    "Patient.identifier[type=MRN].system": PatientMRNIdentifierValueHandler(),
    "Patient.identifier[type=MRN].value": PatientMRNIdentifierValueHandler(),
    "Patient.identifier[type=SSN].system": PatientSSNIdentifierValueHandler(),
    "Patient.identifier[type=SSN].value": PatientSSNIdentifierValueHandler(),
    "Organization.identifier[system=NPI].value": OrganizationIdentiferNPIValueHandler(),
    "Organization.identifier[system=CLIA].value": OrganizationIdentiferCLIAValueHandler(),
    "Practitioner.identifier[system=NPI].value": PractitionerIdentiferNPIValueHandler(),
    "Observation.component[": ObservationComponentHandler()
}