"""
Utility functions for LangGraph development.
"""

from typing import Any, Dict, List, Union
from langchain_core.messages import BaseMessage


def _make_serializable(obj: Any) -> Any:
    """
    Convert LangChain messages and other non-serializable objects to JSON-serializable format.
    
    This function recursively processes objects to ensure they can be serialized to JSON,
    which is necessary for logging and storing results.
    
    Args:
        obj: The object to make serializable (can be a message, dict, list, or primitive)
        
    Returns:
        A JSON-serializable version of the object
    """
    # Handle None
    if obj is None:
        return None
    
    # Handle LangChain BaseMessage objects
    if isinstance(obj, BaseMessage):
        # Convert message to dict using model_dump() for Pydantic v2
        try:
            message_dict = obj.model_dump()
        except AttributeError:
            # Fallback for Pydantic v1
            message_dict = obj.dict()
        
        # Recursively process the dict to handle nested non-serializable objects
        return _make_serializable(message_dict)
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: _make_serializable(value) for key, value in obj.items()}
    
    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    
    # Handle sets
    if isinstance(obj, set):
        return [_make_serializable(item) for item in obj]
    
    # Handle primitive types that are already serializable
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # For any other object, try to convert to string as a fallback
    try:
        # Check if it's already JSON serializable
        import json
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        # If not serializable, convert to string representation
        return str(obj)