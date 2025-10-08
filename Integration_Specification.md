# Overview
This is an Integration Specification for using the "FHIRSheets" project for integration with other projects; such as a web service or external application. Allowing FHIRSheets to act as a tool for generative FHIR data; as a service.

## Entrypoints.

The project is broken into 2 modules.
* fhir_sheets.core - The main processing and handling with integrative steps
* fhir_sheets.cli - A cli tool that uses core for doing the main FHIRSheets processing

For CLI usage; refer to the 'README.md' file as the working guide.

For Core integration the entry point is

```
fhir_sheets.core.conversion.create_transaction_bundle(resource_definition_entities, resource_link_entities, patient_data, index = 0):
```

This function takes in 4 sets of input
* A resource definition entities schema
* A resource link entities schema
* A patient data schema
* An index within the patient data

And creates a transaction bundle consisting of entries, linked together as specified in the resource link entries shcema, AND with data provided by the patient data schema at the specified index

## resource_definition_entities schema
The resource_definition_entities schema is a list of "entity" schemas as follows
```
resource_definition_entities
list:
{
    'Entity Name': String; the name of the entity,
    'Profile(s)': List(String); A list of profile urls the entity uses. ,
    'ResourceType': String; The common name of a base fhir resource the entity is built from
}
```
Using this schema; FHIRSheets understands the baseline name and identity of each entity to build, making up the core blocks of resources that are created for the sheet.
This definition can be found at src/fhir_sheets/core/model/resource_definition_entity.py

## resource_link_entities schema
The resource_link_entities schema is a list of "resource links" schemas as follows
```
resource_link_entities
list:
{
    'DestinationResource': String; entity name which corresponds to the resource_definition_entities that is the target reference,
    'OriginResource': String; entity name which corresponds to the resource_definition_entities that is the source resource making the reference,
    'ReferencePath': String(JsonPath); A simple json path definition that points to where the reference is being created}
}
```
Using this schema, FHIRSheets understand how to link the various entities together on their reference paths to ensure reference integrity within the output bundle
This definition can be found at src/fhir_sheets/core/model/resource_link_entity.py

## cohort_data schema
The cohort_data schema is by far the most complicated of the schema objects. It is a composite object of a list of HeaderEntries, and a list of PatientEntries
```
cohort_data
{
    headers - HeaderEntry: List;
    patients - PatientEntry: List;
}
```

The HeaderEntry describes a set of information that is common across the entire cohort for the field set. Values are not set here, but jsonPathing, vocabulary sets and a common field name are described here.
```
HeaderEntry
dict:
{
    'entityName': String(entityName); must correspond to the Entity Name from the resource_definition schema, points to the entity this filed will be a part of
    'fieldName': String(fieldName); describes a common name to be reused in the patients entry. With the entityName and the fieldName, a composite unique key for the field is created,
    'jsonpath': String(jsonPath); simplified jsonpath, starting with the resourceType name, to describe a path through the json to be setting,
    'valueType': String; the string name of the FHIR Value type being used, which informs FHIRSheets as to the rendering of the values at the path provided. Refer to https://hl7.org/fhir/R4/datatypes.html for a list of all datatypes,
    'values': List(any); the list of actual values per patient; the list should be as long as the num_entries provided. Empty values are accepted as null. Actual python datatypes may vary depending on the fhir valueType described but they may be: String, a careat delimited Address line^city^county^postalcode^state^country, a caret delimited Coding or CodeableConcept System^Code^Display, a quantity value^unit, or a datetime.datetime datastructure in the case of time elements.
    'valuesets': String; A url of the FHIR valueset this field must follow. Not used to validate but used to hint and provide structure if needed.
}
```

The PatientEntry describes an actual realized patient data; using the headerentry and values this is where the finalized data is created per patient.
```
PatientEntry
dict:
{
    key - Tuple[str(EntryName), str(FieldName)]; the keys within the patiententry dictionary must be a tuple of entity name and field name to ensure uniqueness to the domain of entities
    value - Any; The actual value used. Empty values are accepted as null. Actual python datatypes may vary depending on the fhir valueType described in the HeaderEntry but they may be: String, a careat delimited Address line^city^county^postalcode^state^country, a caret delimited Coding or CodeableConcept System^Code^Display, a quantity value^unit, or a datetime.datetime datastructure in the case of time elements.
}
# Jsonpath Help

The jsonpath engine built for FHIRSheets is a custom parsing engine ruleset designed to simplify the FHIRPath and jsonPath definitions in order to simplify pathing definitions for the purpose of generation. It is by no means a completed jsonPath engine but provides enough support for the common use cases

## Jsonpath Examples

Simple pathing
```
Procedure.code
```

Multiple stage pathing
```
Encounter.period.end
```
Simple Indexing on list items
```
Condition.category.[0]
```

Corresponding indexed components
```
RelatedPerson.identifier.[0].value
RelatedPerson.identifier.[0].system
```

Conditional pathing for 1 level deep; presuming the conditional value is resolvable to a string value.
Note that in the generation; this will CREATE the component with the field assigned as well within the resource.
```
Patient.identifier[type=MRN].system
```

Special Handling: OMB Race and Ethnicity. In order to simplify extension handling in common usecases; a general key is provided. Currently the only handler for this is "Race" and "Ethnicity" however this can be extended to more usecases as needed for consiseness sakes
```
Patient.extension[Race].ombCategory.value
Patient.extension[Ethnicity].ombCategory.value
```

Special Handling: DataAbsentReason. The jsonpath Manages the terminology for http://terminology.hl7.org/CodeSystem/data-absent-reason as a special case and matches values as needed without having to provide entire coding since it's so prevalent.
```
Observation.dataAbsentReason
```

Normal Extension Handling. Follow this form for creating extensions normally.
```
Practitioner.telecom.extension[url=http://hl7.org/fhir/us/core/StructureDefinition/us-core-direct].valueBoolean
```