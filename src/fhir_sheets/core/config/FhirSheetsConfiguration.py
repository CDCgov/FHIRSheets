from typing import Any, Dict


class FhirSheetsConfiguration():
    def __init__(self, data: Dict[str, Any]):
        self.preview_mode = data.get('preview_mode', False)
        self.medications_as_reference = data.get('medications_as_reference', False)
    
    def __repr__(self) -> str:
        return (f"FhirSheetsConfiguration("
                f"preview_mode={self.preview_mode}, "
                f"medications_as_reference={self.medications_as_reference})")