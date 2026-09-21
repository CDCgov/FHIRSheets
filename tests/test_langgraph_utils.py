"""
Tests for the langgraph_dev utility functions.
"""

import json
import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from src.langgraph_dev.utils import _make_serializable


def test_make_serializable_with_human_message():
    """Test that HumanMessage objects are properly serialized."""
    message = HumanMessage(content="Hello, world!")
    result = _make_serializable(message)
    
    # Should be a dict
    assert isinstance(result, dict)
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Should contain the content
    assert result["content"] == "Hello, world!"
    assert result["type"] == "human"


def test_make_serializable_with_ai_message():
    """Test that AIMessage objects are properly serialized."""
    message = AIMessage(content="I'm an AI assistant.")
    result = _make_serializable(message)
    
    # Should be a dict
    assert isinstance(result, dict)
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Should contain the content
    assert result["content"] == "I'm an AI assistant."
    assert result["type"] == "ai"


def test_make_serializable_with_tool_message():
    """Test that ToolMessage objects are properly serialized."""
    message = ToolMessage(content="Tool result", tool_call_id="call_123")
    result = _make_serializable(message)
    
    # Should be a dict
    assert isinstance(result, dict)
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Should contain the content
    assert result["content"] == "Tool result"
    assert result["tool_call_id"] == "call_123"


def test_make_serializable_with_list_of_messages():
    """Test that a list of messages is properly serialized."""
    messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
        SystemMessage(content="System message")
    ]
    
    result = _make_serializable(messages)
    
    # Should be a list
    assert isinstance(result, list)
    assert len(result) == 3
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Check each message
    assert result[0]["content"] == "Hello"
    assert result[0]["type"] == "human"
    assert result[1]["content"] == "Hi there!"
    assert result[1]["type"] == "ai"
    assert result[2]["content"] == "System message"
    assert result[2]["type"] == "system"


def test_make_serializable_with_dict_containing_messages():
    """Test that a dict containing messages is properly serialized."""
    data = {
        "messages": [
            HumanMessage(content="Question"),
            AIMessage(content="Answer")
        ],
        "metadata": {
            "timestamp": "2024-01-01",
            "user_id": 123
        }
    }
    
    result = _make_serializable(data)
    
    # Should be a dict
    assert isinstance(result, dict)
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Check structure
    assert len(result["messages"]) == 2
    assert result["messages"][0]["content"] == "Question"
    assert result["messages"][1]["content"] == "Answer"
    assert result["metadata"]["timestamp"] == "2024-01-01"
    assert result["metadata"]["user_id"] == 123


def test_make_serializable_with_nested_messages():
    """Test that deeply nested structures with messages are properly serialized."""
    data = {
        "level1": {
            "level2": {
                "messages": [
                    HumanMessage(content="Nested message")
                ],
                "values": [1, 2, 3]
            }
        }
    }
    
    result = _make_serializable(data)
    
    # Should be JSON serializable
    json_str = json.dumps(result)
    assert json_str is not None
    
    # Check nested structure
    assert result["level1"]["level2"]["messages"][0]["content"] == "Nested message"
    assert result["level1"]["level2"]["values"] == [1, 2, 3]