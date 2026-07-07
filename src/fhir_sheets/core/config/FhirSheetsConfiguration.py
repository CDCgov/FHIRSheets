import time
from typing import Any, Dict, List, Tuple


class FhirSheetsConfiguration():
    def __init__(self, data: Dict[str, Any]):
        self.preview_mode = data.get('preview_mode', False)
        self.medications_as_reference = data.get('medications_as_reference', False)
        self.random_seed = data.get('random_seed', int(time.time() * 1000))
        self.build_empty_resources = data.get('build_empty_resources', False)
        
        # Toggle for automatic default resource links
        self.enable_default_resource_links = data.get('enable_default_resource_links', True)
        
        # Default resource references: (source_type, destination_type, field_name)
        self.default_resource_references = data.get('default_resource_references', [
            ('allergyintolerance', 'patient', 'patient'),
            ('allergyintolerance', 'practitioner', 'asserter'),
            ('careplan', 'goal', 'goal'),
            ('careplan', 'patient', 'subject'),
            ('careplan', 'practitioner', 'performer'),
            ('diagnosticreport', 'careteam', 'performer'),
            ('diagnosticreport', 'imagingStudy', 'imagingStudy'),
            ('diagnosticreport', 'observation', 'result'),
            ('diagnosticreport', 'organization', 'performer'),
            ('diagnosticreport', 'practitioner', 'performer'),
            ('diagnosticreport', 'practitionerrole', 'performer'),
            ('diagnosticreport', 'specimen', 'specimen'),
            ('encounter', 'condition', 'reasonReference'),
            ('encounter', 'location', 'location'),
            ('encounter', 'organization', 'serviceProvider'),
            ('encounter', 'patient', 'subject'),
            ('goal', 'condition', 'addresses'),
            ('goal', 'patient', 'subject'),
            ('immunization', 'patient', 'patient'),
            ('immunization', 'practitioner', 'performer'),
            ('immunization', 'organization', 'manufacturer'),
            ('medicationrequest', 'medication', 'medicationReference'),
            ('medicationrequest', 'patient', 'subject'),
            ('medicationrequest', 'practitioner', 'requester'),
            ('observation', 'device', 'device'),
            ('observation', 'patient', 'subject'),
            ('observation', 'practitioner', 'performer'),
            ('observation', 'practitionerrole', 'performer'),
            ('observation', 'organization', 'performer'),
            ('observation', 'careteam', 'performer'),
            ('observation', 'patient', 'performer'),
            ('observation', 'relatedperson', 'performer'),
            ('observation', 'specimen', 'specimen'),
            ('procedure', 'condition', 'reasonReference'),
            ('procedure', 'device', 'usedReference'),
            ('procedure', 'location', 'location'),
            ('procedure', 'patient', 'subject'),
            ('procedure', 'practitioner', 'performer'),
        ])
        
        # Array-type references: (origin_resource, destination_resource, reference_path)
        self.array_type_references = data.get('array_type_references', [
            ('diagnosticreport', 'specimen', 'specimen'),
            ('diagnosticreport', 'practitioner', 'performer'),
            ('diagnosticreport', 'practitionerrole', 'performer'),
            ('diagnosticreport', 'organization', 'performer'),
            ('diagnosticreport', 'careteam', 'performer'),
            ('diagnosticreport', 'observation', 'result'),
            ('diagnosticreport', 'imagingStudy', 'imagingStudy'),
            ('encounter', 'condition', 'reasonReference'),
            ('observation', 'practitioner', 'performer'),
            ('observation', 'practitionerrole', 'performer'),
            ('observation', 'organization', 'performer'),
            ('observation', 'careteam', 'performer'),
            ('observation', 'patient', 'performer'),
            ('observation', 'relatedperson', 'performer'),
            ('procedure', 'condition', 'reasonReference'),
        ])
    
    def __repr__(self) -> str:
        return (f"FhirSheetsConfiguration("
                f"preview_mode={self.preview_mode}, "
                f"medications_as_reference={self.medications_as_reference}, "
                f"random_seed={self.random_seed}, "
                f"build_empty_resources={self.build_empty_resources}, "
                f"enable_default_resource_links={self.enable_default_resource_links}, "
                f"default_resource_references={len(self.default_resource_references)} items, "
                f"array_type_references={len(self.array_type_references)} items)")