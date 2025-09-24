import re
from datetime import datetime, time, timezone

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
    # Removing white space
    if isinstance(value, str):
        value = value.strip()
    # Checking for null or empty string values. If so; we do not construct the value
    if not value:
        return final_struct
    # If the valueType is not provide, do not construct the value.
    if valueType is None:
        return final_struct
    # Swtich case for valueType to construct a value
    try:
        if valueType.lower() == 'address':
            address_value = parse_flexible_address(value)
            if address_value:
                final_struct[key] = address_value
        elif valueType.lower() == 'base64binary':
            final_struct[key] = value
        elif valueType.lower() == 'boolean':
            final_struct[key] = bool(value)
        elif valueType.lower() == 'codeableconcept':
            final_struct[key] = caret_delimited_string_to_codeableconcept(value)
        elif valueType.lower() == 'code':
            match = re.search(type_regexes['code'], value)
            final_struct[key] = match.group(0) if match else ''
        elif valueType.lower() == 'coding':
            final_struct[key] = caret_delimited_string_to_coding(value)
        elif valueType.lower() == 'date':
            if isinstance(value, datetime):
                final_struct[key] = value.date()
            elif isinstance(value, str):
                final_struct[key] = parse_iso8601_date(value).replace(tzinfo=timezone.utc)
        elif valueType.lower() == 'datetime':
            if isinstance(value, datetime):
                final_struct[key] = value.replace(tzinfo=timezone.utc)
            else:
                final_struct[key] = parse_iso8601_datetime(value).replace(tzinfo=timezone.utc)
        elif valueType.lower() == 'decimal':
            final_struct[key] = value
        elif valueType.lower() == 'id':
            match = re.search(value, type_regexes['id'])
            final_struct[key] = match.group(0) if match else ''
        elif valueType.lower() == 'instant':
            if isinstance(value, datetime):
                final_struct[key] = value.replace(tzinfo=timezone.utc)
            else:
                final_struct[key] = final_struct[key] = parse_iso8601_instant(value).replace(tzinfo=timezone.utc)
        elif valueType.lower() == 'integer':
            match = re.search(value, type_regexes['integer'])
            final_struct[key] = int(match.group(0)) if match else 0
        elif valueType.lower() == 'oid':
            match = re.search(value, type_regexes['oid'])
            final_struct[key] = match.group(0) if match else ''
        elif valueType.lower() == 'positiveInt':
            match = re.search(value, type_regexes['positiveInt'])
            final_struct[key] = int(match.group(0)) if match else 0
        elif valueType.lower() == 'quantity':
            final_struct[key] = string_to_quantity(value)
        elif valueType.lower() == 'string':
            final_struct[key] = value
        elif valueType.lower() == 'string[]':
            if not key in final_struct:
                final_struct[key] = [value]
            else:
                final_struct[key].append(value)
        elif valueType.lower() == 'time':
            if isinstance(time):
                final_struct[key] = value
            else:
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
        elif valueType.lower() == 'coding':
            if not isinstance(final_struct, list):
                final_struct = []
            final_struct.append(value)
        else:
            print(f"ERROR: - Rending Value - {key} - {value} - {valueType} - Saw a valueType of '{valueType}' unsupported in current formatting")
    except ValueError as e:
        print(e)
    return final_struct
        
def parse_iso8601_date(input_string):
    # Regular expression to match ISO 8601 format with optional timezone 'Z'
    pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    else:
        raise ValueError(f"Input string '{input_string}' is not in the valid ISO 8601 date format")

def parse_iso8601_datetime(input_string):
    # Regular expression to match ISO 8601 format with optional timezone 'Z'
    pattern = r'(\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(Z)?)?)'
    match = re.search(pattern, input_string)
    # Check if the input string matches the pattern
    if match:
        # Convert to datetime object
        if input_string.endswith('Z'):
            # If it has 'Z', convert to UTC
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError: # If it fails (because the time part is missing), parse the date-only format and set time to midnight
                try:
                    parsed_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                    parsed_datetime = parsed_date.replace(hour=0, minute=0, second=0)
                    return parsed_datetime
                except ValueError: # Neither format worked so catch an entire error
                    raise ValueError(f"Input string '{input_string}' is not in the valid ISO 8601 format date or datetime format")
        else:
            # Otherwise, just convert without timezone
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError: # If it fails (because the time part is missing), parse the date-only format and set time to midnight
                try:
                    parsed_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                    parsed_datetime = parsed_date.replace(hour=0, minute=0, second=0)
                    return parsed_datetime
                except ValueError: # Neither format worked so catch an entire error
                    raise ValueError(f"Input string '{input_string}' is not in the valid ISO 8601 format date or datetime format")
    else:
        raise ValueError(f"Input string '{input_string}' is not in the valid ISO 8601 format date or datetime format")
    
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
        raise ValueError(f"Input string '{input_string}' is not in the valid ISO 8601 instant format")
    
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
        
        return datetime.time(hour=hours, minute=minutes, second=int(seconds), microsecond=int((seconds % 1) * 1_000_000))
    else:
        raise ValueError(f"Input string '{input_string}' is not in the valid time format")
    
def parse_flexible_address(address):
    # Attempt to capture postal code, which is often at the end and typically numeric (though it may vary internationally)
    postal_code_pattern = r'(?P<postalCode>\d{5}(?:-\d{4})?|)'
    
    # State is typically a two-letter code (though this may vary internationally as well)
    state_pattern = r'(?P<state>[A-Za-z]{2}|)'
    
    # This captures a country after a comma (or space-separated) if it's present
    country_pattern = r'(?:\s*(?P<country>[\w\s]+|))?$'
    
    # Compile the full pattern to match the postal code, state, and country
    full_pattern = rf'^(?P<line>.*?)\^(?P<city>.*?)\^(?P<district>.*?)\^{postal_code_pattern}\^{state_pattern}\^{country_pattern}'
    
    match = re.search(full_pattern, address)
    
    if match:
        # Extract the components found in the regex
        result = {k: v for k, v in match.groupdict().items() if v not in ("", None)}
        if not result:
            return None
        #Assign the line as an array of 1
        if result['line'] and isinstance(result['line'], str):
            result['line'] = [result['line']]
        return result
    else:
        return None  # Return None if the format doesn't match
    
def caret_delimited_string_to_codeableconcept(caret_delimited_str):
    # Split the string by '~' to separate multiple codings
    codings = caret_delimited_str.split('~')
    
    # Initialize the CodeableConcept dictionary
    codeable_concept = {"coding": []}
    
    # Loop over each coding section
    for coding_str in codings:
        # Split each part by '^' to get system, code, and display (optionally text at the end)
        parts = coding_str.split('^')
        
        # Create a coding dictionary from the components
        coding_dict = {}
        if len(parts) > 0:
            coding_dict['system'] = parts[0] if parts[0] else ''
        if len(parts) > 1:
            coding_dict['code'] = parts[1] if parts[1] else ''
        if len(parts) > 2:
            coding_dict['display'] = parts[2] if parts[2] else ''
        
        # Add coding to the 'coding' list in CodeableConcept
        codeable_concept['coding'].append(coding_dict)
    
    # Check if the last element contains 'text' (for the entire CodeableConcept)
    if len(parts) == 4:
        codeable_concept['text'] = parts[3]
    return codeable_concept

def caret_delimited_string_to_coding(caret_delimited_str):
    # Split the string by '~' to separate multiple codings
    
    # Initialize the CodeableConcept dictionary
    coding = {}
    
    parts = caret_delimited_str.split('^')
    
    # Create a coding dictionary from the components
    if len(parts) > 0:
        coding['system'] = parts[0] if parts[0] else ''
    if len(parts) > 1:
        coding['code'] = parts[1] if parts[1] else ''
    if len(parts) > 2:
        coding['display'] = parts[2] if parts[2] else ''
    return coding

def string_to_quantity(quantity_str):
    # Split the string into value and unit by whitespace
    parts = quantity_str.split('^',maxsplit=1)
    
    # Initialize the Quantity dictionary
    quantity = {}
    
    # First part is the value (convert to float)
    if len(parts) > 0:
        quantity['value'] = float(parts[0])
    
    # Second part is the unit (if present)
    if len(parts) > 1:
        quantity['unit'] = parts[1]
        quantity['system'] = 'http://unitsofmeasure.org'
        quantity['code'] = parts[1]
    
    
    return quantity