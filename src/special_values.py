
from abc import ABC, abstractmethod

# Define an abstract base class
class AbstractCustomValueHandler(ABC):
    
    @abstractmethod
    def assign_value(self, final_struct, key, value):
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
    def assign_value(self, final_struct, key, value):
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
          "display" : "Non Hispanic or Latino"
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
    def assign_value(self, final_struct, key, value):
        #Retrieve the ethncitiy extension if it exists; make it if it does not.
        if 'extension' not in final_struct:
            final_struct['extension'] = []
        ethnicity_block = utilFindExtensionWithURL(final_struct['extension'], 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')
        if ethnicity_block is None:
            ethnicity_block = self.initial_ethnicity_json
            final_struct['extension'].append(ethnicity_block)
        for race_key, race_structure in self.omb_categories.items():
            if value.strip().lower() == race_key:
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
    def assign_value(self, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'extension' not in final_struct:
            final_struct['extension'] = []
        birthsex_block = utilFindExtensionWithURL(final_struct['extension'], 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')
        if birthsex_block is None:
            birthsex_block = self.birth_sex_block
            birthsex_block['valueCode'] = value
            final_struct['extension'].append(birthsex_block)
        pass
      
class OrganizationIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block = {
      "system" : "http://hl7.org.fhir/sid/us-npi",
      "value" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "http://hl7.org.fhir/sid/us-npi"), None)
        if identifier_block is None:
          identifier_block = self.npi_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = value
        pass
      
class OrganizationIdentiferCLIAValueHandler(AbstractCustomValueHandler):
    clia_identifier_block = {
      "system" : "urn:oid:2.16.840.1.113883.4.7",
      "value" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "urn:oid:2.16.840.1.113883.4.7"), None)
        if identifier_block is None:
          identifier_block = self.clia_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = value
        pass
      
class PractitionerIdentiferNPIValueHandler(AbstractCustomValueHandler):
    npi_identifier_block = {
      "system" : "http://hl7.org.fhir/sid/us-npi",
      "value" : "$value"
    }
    #Assigna birthsex extension
    def assign_value(self, final_struct, key, value):
        #Retrieve the birthsex extension if it exists; make it if it does not.
        if 'identifier' not in final_struct:
            final_struct['identifier'] = []
        identifier_block = next((entry for entry in final_struct['identifier'] if entry['system'] == "http://hl7.org.fhir/sid/us-npi"), None)
        if identifier_block is None:
          identifier_block = self.npi_identifier_block
          final_struct['identifier'].append(identifier_block)
        identifier_block['value'] = value
        pass
      
def utilFindExtensionWithURL(extension_block, url):
    for extension in extension_block:
        if "url" in extension and extension['url'] == url:
            return extension
        return None
#Data dictionary of jsonpaths to match vs classes that need to be called
custom_handlers = {
    "Patient.extension[Race].ombCategory": PatientRaceExtensionValueHandler(),
    "Patient.extension[Ethnicity].ombCategory": PatientEthnicityExtensionValueHandler(),
    "Patient.extension[Birthsex].value": PatientBirthSexExtensionValueHandler(),
    "Organization.identifier[system=NPI].value": OrganizationIdentiferNPIValueHandler(),
    "Organization.identifier[system=CLIA].value": OrganizationIdentiferCLIAValueHandler(),
    "Practitioner.identifier[system=NPI].value": PractitionerIdentiferNPIValueHandler()
}