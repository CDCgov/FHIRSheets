import re
from datetime import datetime

#Dictionary of regexes
type_regexes = {
    'code': '[^\s]+( [^\s]+)*',
    'decimal': '-?(0|[1-9][0-9]{0,17})(\.[0-9]{1,17})?([eE][+-]?[0-9]{1,9}})?',
    'id': '[A-Za-z0-9\-\.]{1,64}',
    'integer': '[0]|[-+]?[1-9][0-9]*',
    'oid': 'urn:oid:[0-2](\.(0|[1-9][0-9]*))+',
    'positiveInt': '[1-9][0-9]*',
    'unsignedInt':'[0]|([1-9][0-9]*)',
    'uuid':'urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
}
# Assign final_struct[key] to value; with formatting given the valueType
def assign_value(final_struct, key, value, valueType):
    #TODO: Handle cases with no valuetype.
    if valueType is None:
        return final_struct
    if valueType.lower() == 'boolean':
        if 'true' in value:
            final_struct[key] = True
        else:
            final_struct[key] = False
    elif valueType.lower() == 'code':
        match = re.search(value, type_regexes['code'])
        final_struct[key] = match.group(0) if match else ''
    elif valueType.lower() == 'date':
        final_struct[key] = parse_iso8601_date(value)
    elif valueType.lower() == 'datetime':
        final_struct[key] = parse_iso8601_datetime(value)
    elif valueType.lower() == 'decimal':
        match = re.search(value, type_regexes['decimal'])
        final_struct[key] = match.group(0) if match else ''
    elif valueType.lower() == 'id':
        match = re.search(value, type_regexes['id'])
        final_struct[key] = match.group(0) if match else ''
    elif valueType.lower() == 'instant':
        final_struct[key] = final_struct[key] = parse_iso8601_instant(value)
    elif valueType.lower() == 'integer':
        match = re.search(value, type_regexes['integer'])
        final_struct[key] = int(match.group(0)) if match else 0
    elif valueType.lower() == 'oid':
        match = re.search(value, type_regexes['oid'])
        final_struct[key] = match.group(0) if match else ''
    elif valueType.lower() == 'positiveInt':
        match = re.search(value, type_regexes['positiveInt'])
        final_struct[key] = int(match.group(0)) if match else 0
    elif valueType.lower() == 'string':
        final_struct[key] = value
    elif valueType.lower() == 'string[]':
        if not key in final_struct:
            final_struct[key] = [value]
        else:
            final_struct[key].append(value)
    elif valueType.lower() == 'time':
        final_struct[key] = parse_iso8601_time(value)
    elif valueType.lower() == 'unsignedInt':
        match = re.search(value, type_regexes['unsignedInt'])
        final_struct[key] = int(match.group(0)) if match else 0
    elif valueType.lower() == 'uri':
        final_struct[key] = value
    elif valueType.lower() == 'url':
        final_struct[key] = value
    elif valueType.lower() == 'uuid':
        match = re.search(value, type_regexes['uuid'])
        final_struct[key] = match.group(0) if match else ''
    return final_struct
        
def parse_iso8601_date(input_string):
    # Regular expression to match ISO 8601 format with optional timezone 'Z'
    pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    else:
        raise ValueError("Input string is not in the valid ISO 8601 date format")

def parse_iso8601_datetime(input_string):
    # Regular expression to match ISO 8601 format with optional timezone 'Z'
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z)?)'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        # Convert to datetime object
        if input_string.endswith('Z'):
            # If it has 'Z', convert to UTC
            return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        else:
            # Otherwise, just convert without timezone
            return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S')
    else:
        raise ValueError("Input string is not in the valid ISO 8601 format")
    
def parse_iso8601_instant(input_string):
    # Regular expression to match ISO 8601 instant format with optional milliseconds and 'Z'
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?(Z)?)'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        # If it ends with 'Z', it's UTC
        if input_string.endswith('Z'):
            if '.' in input_string:
                # With milliseconds
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
            else:
                # Without milliseconds
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        else:
            if '.' in input_string:
                # With milliseconds
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S.%f')
            else:
                # Without milliseconds
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S')
    else:
        raise ValueError("Input string is not in the valid ISO 8601 instant format")
    
def parse_iso8601_time(input_string):
    # Regular expression to match the time format HH:MM:SS or HH:MM:SS.ssssss
    pattern = r'((?:[01][0-9]|2[0-3]):[0-5][0-9]:([0-5][0-9]|60)(\.[0-9]{1,9})?)'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        # Parse the time
        time_parts = match.group(1).split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])  # This can handle the fractional part
        
        return time(hour=hours, minute=minutes, second=int(seconds), microsecond=int((seconds % 1) * 1_000_000))
    else:
        raise ValueError("Input string is not in the valid time format")