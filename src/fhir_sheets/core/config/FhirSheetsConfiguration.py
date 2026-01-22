import time
from typing import Any, Dict


class FhirSheetsConfiguration():
    def __init__(self, data: Dict[str, Any]):
        self.preview_mode = data.get('preview_mode', False)
        self.medications_as_reference = data.get('medications_as_reference', False)
        self.random_seed = data.get('random_seed', int(time.time() * 1000))
        self.build_empty_resources = data.get('build_empty_resources', False)
    
    def __repr__(self) -> str:
        return (f"FhirSheetsConfiguration("
                f"preview_mode={self.preview_mode}, "
                f"medications_as_reference={self.medications_as_reference}, "
                f"random_seed={self.random_seed}, "
                f"build_empty_resources={self.build_empty_resources})")