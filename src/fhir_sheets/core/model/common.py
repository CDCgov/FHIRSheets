
from typing import Any, Dict, List


def get_value_from_keys(data: Dict[str, Any], keys: List[str], default: Any) -> Any:
        lower_data = {k.lower(): v for k, v in data.items()}
        """Helper function to find the first existing key and return its value."""
        for key in keys:
            lower_key = key.lower()
            if lower_key in lower_data:
                return lower_data[lower_key]
        return default