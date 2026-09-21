"""
FHIRSheets AI Agent

This module provides the main AI agent that orchestrates FHIR resource generation
using LangGraph and LLM capabilities.
"""

from typing import Optional, List, Dict, Any, Literal
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from .config import get_config, LangGraphConfig
from .tools.fhirsheets_xlsx_tool import FhirSheetsXlsxToolkit
from .tools.fhirsheets_resource_builder_tool import FhirSheetsResourceBuilderToolkit
from .utils import _make_serializable

# Set up logger for tool invocations
logger = logging.getLogger(__name__)


class FHIRSheetsAIAgent:
    """
    AI Agent for FHIR resource generation using natural language.
    
    This agent uses LangGraph to orchestrate tool calls and generate FHIR resources
    based on natural language instructions.
    """
    
    def __init__(
        self,
        config: Optional[LangGraphConfig] = None,
        working_dir: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize the FHIRSheets AI Agent.
        
        Args:
            config: Optional LangGraphConfig instance. If not provided, loads from environment.
            working_dir: Working directory for Excel files. Overrides config if provided.
            verbose: Enable verbose logging
        """
        # Load configuration
        self.config = config or get_config()
        
        # Validate configuration
        is_valid, error = self.config.validate()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {error}")
        
        # Set working directory
        if working_dir:
            self.working_dir = working_dir
        else:
            self.working_dir = self.config.fhirsheets_working_dir
        
        self.verbose = verbose or self.config.langgraph_verbose
        
        # Initialize LLM
        self.llm = self._create_llm()
        
        # Initialize tools
        self.xlsx_toolkit = FhirSheetsXlsxToolkit(working_dir=self.working_dir)
        self.resource_builder_toolkit = FhirSheetsResourceBuilderToolkit(xlsx_toolkit=self.xlsx_toolkit)
        
        # Get all tools (resource_builder includes both high-level and low-level tools)
        self.tools = self.resource_builder_toolkit.get_tools()
        
        # Create agent
        self.memory = MemorySaver()
        self.agent = create_react_agent(
            self.llm,
            self.tools,
            checkpointer=self.memory
        )
        
        # System prompt
        self.system_prompt = self._create_system_prompt()
        
        if self.verbose:
            print(f"FHIRSheets AI Agent initialized")
            print(f"  LLM Provider: {self.config.get_llm_provider()}")
            print(f"  Model: {self.config.openai_model_name}")
            print(f"  Working Directory: {self.working_dir}")
            print(f"  Available Tools: {len(self.tools)}")
    
    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the LLM based on configuration."""
        provider = self.config.get_llm_provider()
        
        if provider == "openai":
            return ChatOpenAI(
                model=self.config.openai_model_name,
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_api_base,
                temperature=0,
                streaming=True
            )
        elif provider == "azure":
            return ChatOpenAI(
                model=self.config.azure_openai_deployment_name,
                api_key=self.config.azure_openai_api_key,
                azure_endpoint=self.config.azure_openai_endpoint,
                api_version=self.config.azure_openai_api_version,
                temperature=0,
                streaming=True
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are a FHIR resource generation assistant. You help users create FHIR-compliant 
healthcare data by generating Excel templates and FHIR bundles.

Your capabilities include:
1. Creating new FHIR Excel files from templates
2. Adding resource definitions (Patient, Observation, Condition, etc.)
3. Populating patient data with healthcare information
4. Creating resource links between entities
5. Generating FHIR bundles from completed Excel files

When working with resources:
- Use entity names that are descriptive (e.g., "PrimaryPatient", "DiabetesDiagnosis")
- Patient row indices are 0-based (first patient is row 0)
- Always create resource definitions before adding data
- Use appropriate FHIR profiles (US Core when applicable)
- Link related resources together (e.g., link Observations to Patients)

Be helpful, precise, and ensure all generated data is FHIR-compliant."""
    
    def run(
        self,
        user_input: str,
        thread_id: str = "default",
        stream: bool = True
    ) -> Dict[str, Any]:
        """
        Run the agent with user input.
        
        Args:
            user_input: Natural language instruction from the user
            thread_id: Thread ID for conversation continuity
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the agent's response and any generated artifacts
        """
        # Prepare messages
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # Configure agent execution
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": self.config.langgraph_max_iterations
        }
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"User: {user_input}")
            print(f"{'='*60}\n")
        
        # Run agent
        if stream:
            return self._run_streaming(messages, config)
        else:
            return self._run_non_streaming(messages, config)
    
    def _run_streaming(self, messages: List, config: Dict) -> Dict[str, Any]:
        """Run agent with streaming output."""
        final_response = None
        chunk = None
        
        for chunk in self.agent.stream({"messages": messages}, config, stream_mode="values"):
            if "messages" in chunk:
                last_message = chunk["messages"][-1]
                
                # Log tool invocations
                if isinstance(last_message, AIMessage) and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        tool_id = tool_call.get("id", "unknown")
                        
                        logger.info(f"Tool Invoked: {tool_name}")
                        logger.debug(f"  Tool ID: {tool_id}")
                        logger.debug(f"  Arguments: {tool_args}")
                        
                        if self.verbose:
                            print(f"\n🔧 Tool Invoked: {tool_name}")
                            print(f"   Arguments: {tool_args}")
                
                # Log tool results and check for errors
                if isinstance(last_message, ToolMessage):
                    logger.info(f"Tool Result for {last_message.name}")
                    logger.debug(f"  Content: {last_message.content}")
                    
                    # Check if tool execution failed
                    tool_error = None
                    try:
                        import json
                        result = json.loads(last_message.content)
                        if isinstance(result, dict) and not result.get("success", True):
                            tool_error = result.get("error", "Tool execution failed")
                    except:
                        pass
                    
                    if self.verbose:
                        print(f"\n✓ Tool Result: {last_message.name}")
                        # Try to parse and pretty-print JSON results
                        try:
                            import json
                            result = json.loads(last_message.content)
                            if isinstance(result, dict):
                                if result.get("success"):
                                    print(f"   Status: Success")
                                    for key, value in result.items():
                                        print(f"   [{key}]: [{value}]")
                                else:
                                    print(f"   Status: Failed")
                                    if "error" in result:
                                        print(f"   Error: {result['error']}")
                        except:
                            # If not JSON, just show truncated content
                            content_preview = last_message.content[:100]
                            if len(last_message.content) > 100:
                                content_preview += "..."
                            print(f"   Result: {content_preview}")
                    
                    # If tool failed, stop execution and return error
                    if tool_error:
                        logger.error(f"Tool execution failed: {tool_error}")
                        return {
                            "response": f"Tool execution failed: {tool_error}",
                            "messages": _make_serializable(chunk.get("messages", [])),
                            "success": False,
                            "error": tool_error
                        }
                
                if isinstance(last_message, AIMessage):
                    if last_message.content and self.verbose:
                        print(last_message.content)
                    final_response = last_message
        
        result = {
            "response": final_response.content if final_response else "No response generated",
            "messages": _make_serializable(chunk.get("messages", []) if chunk else []),
            "success": True
        }
        return result
    
    def _run_non_streaming(self, messages: List, config: Dict) -> Dict[str, Any]:
        """Run agent without streaming."""
        result = self.agent.invoke({"messages": messages}, config)
        
        # Log tool invocations from the message history and check for errors
        for message in result.get("messages", []):
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id", "unknown")
                    
                    logger.info(f"Tool Invoked: {tool_name}")
                    logger.debug(f"  Tool ID: {tool_id}")
                    logger.debug(f"  Arguments: {tool_args}")
                    
                    if self.verbose:
                        print(f"\n🔧 Tool Invoked: {tool_name}")
                        print(f"   Arguments: {tool_args}")
            
            if isinstance(message, ToolMessage):
                logger.info(f"Tool Result for {message.name}")
                logger.debug(f"  Content: {message.content}")
                
                # Check if tool execution failed
                tool_error = None
                try:
                    import json
                    result_data = json.loads(message.content)
                    if isinstance(result_data, dict) and not result_data.get("success", True):
                        tool_error = result_data.get("error", "Tool execution failed")
                except:
                    pass
                
                if self.verbose:
                    print(f"\n✓ Tool Result: {message.name}")
                    try:
                        import json
                        result_data = json.loads(message.content)
                        if isinstance(result_data, dict):
                            if result_data.get("success"):
                                print(f"   Status: Success")
                                if "message" in result_data:
                                    print(f"   Message: {result_data['message']}")
                            else:
                                print(f"   Status: Failed")
                                if "error" in result_data:
                                    print(f"   Error: {result_data['error']}")
                    except:
                        content_preview = message.content[:100]
                        if len(message.content) > 100:
                            content_preview += "..."
                        print(f"   Result: {content_preview}")
                
                # If tool failed, stop execution and return error
                if tool_error:
                    logger.error(f"Tool execution failed: {tool_error}")
                    return {
                        "response": f"Tool execution failed: {tool_error}",
                        "messages": _make_serializable(result.get("messages", [])),
                        "success": False,
                        "error": tool_error
                    }
        
        final_message = result["messages"][-1]
        
        if self.verbose and isinstance(final_message, AIMessage):
            print(final_message.content)
        
        result_dict = {
            "response": final_message.content if isinstance(final_message, AIMessage) else str(final_message),
            "messages": _make_serializable(result.get("messages", [])),
            "success": True
        }
        return result_dict
    
    def chat(self, thread_id: str = "default"):
        """
        Start an interactive chat session.
        
        Args:
            thread_id: Thread ID for conversation continuity
        """
        print("\n" + "="*60)
        print("FHIRSheets AI Agent - Interactive Mode")
        print("="*60)
        print("Type your instructions or 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break
                
                self.run(user_input, thread_id=thread_id, stream=True)
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
    
    def get_current_file_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current working file."""
        result = self.xlsx_toolkit.get_current_file.invoke({})
        return result if result.get("success") else None
    
    def list_tools(self) -> List[str]:
        """List all available tools."""
        return [tool.name for tool in self.tools]


def create_agent(
    working_dir: Optional[str] = None,
    verbose: bool = True,
    config: Optional[LangGraphConfig] = None
) -> FHIRSheetsAIAgent:
    """
    Factory function to create a FHIRSheets AI Agent.
    
    Args:
        working_dir: Working directory for Excel files
        verbose: Enable verbose logging
        config: Optional configuration object
        
    Returns:
        Configured FHIRSheetsAIAgent instance
    """
    return FHIRSheetsAIAgent(
        config=config,
        working_dir=working_dir,
        verbose=verbose
    )