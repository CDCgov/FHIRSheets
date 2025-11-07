
import orjson
from src.fhir_sheets.core.fhir_formatting import caret_delimited_string_to_codeableconcept, parse_flexible_address, parse_iso8601_date, parse_iso8601_datetime, parse_iso8601_instant, string_to_quantity


def test_parse_iso8601_date():
    input = "2025-10-21"
    date = parse_iso8601_date(input)
    assert date.year == 2025
    assert date.month == 10
    assert date.day == 21
    
def test_parse_iso8601_date_and_check_json_dump():
    input = "2017-05-15"
    date = parse_iso8601_date(input)
    assert date.year == 2017
    assert date.month == 5
    assert date.day == 15
    json_string = orjson.dumps(date)
    print(json_string)
    assert json_string == b'"2017-05-15"'
    
def test_parse_iso8601_datetime():
    input = "2025-10-21T11:59:34"
    date = parse_iso8601_datetime(input)
    assert date.year == 2025
    assert date.month == 10
    assert date.day == 21
    assert date.hour == 11
    assert date.minute == 59
    assert date.second == 34
    
def test_parse_iso8601_instant():
    input = "2025-10-21T11:59:34.123"
    date = parse_iso8601_instant(input)
    assert date.year == 2025
    assert date.month == 10
    assert date.day == 21
    assert date.hour == 11
    assert date.minute == 59
    assert date.second == 34
    assert date.microsecond == 123000
    
def test_parse_address():
    address_result = parse_flexible_address("1234 Main Street^Atlanta^Fulton^30345^GA^USA")
    assert address_result is not None
    assert type(address_result['line']) == list
    
def test_caret_delimited_string_to_codeableconcept():
    concept_struct = caret_delimited_string_to_codeableconcept("http://loinc.org^2345^Some Concept Display")
    assert concept_struct['coding']
    assert len(concept_struct['coding']) == 1
    assert concept_struct['coding'][0]['code'] == '2345'
    assert concept_struct['coding'][0]['system'] == 'http://loinc.org'
    assert concept_struct['coding'][0]['display'] == 'Some Concept Display'
    
def test_string_to_quantity():
    quantity = string_to_quantity("12^dm/L")
    assert quantity['value'] == 12
    assert quantity['unit'] == 'dm/L'