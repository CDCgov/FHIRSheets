"""
Configuration loader for LangGraph development environment.

This module loads configuration from environment variables and .env files.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class LangGraphConfig:
    """Configuration class for LangGraph development environment."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration by loading from environment variables.
        
        Args:
            env_file: Optional path to .env file. If not provided, looks for .env
                     in the langgraph_dev directory.
        """
        # Determine .env file location
        if env_file:
            env_path = Path(env_file)
        else:
            # Look for .env in the same directory as this file
            env_path = Path(__file__).parent / ".env"
        
        # Load .env file if it exists
        if env_path.exists():
            load_dotenv(env_path)
            self._env_file_loaded = True
            self._env_file_path = str(env_path)
        else:
            self._env_file_loaded = False
            self._env_file_path = None
        
        # Load OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
        
        # Load Azure OpenAI configuration (alternative)
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Load FHIRSheets configuration
        self.fhirsheets_working_dir = os.getenv("FHIRSHEETS_WORKING_DIR", "./output")
        self.fhirsheets_config_path = os.getenv("FHIRSHEETS_CONFIG_PATH")
        
        # Load LangGraph configuration
        self.langgraph_verbose = os.getenv("LANGGRAPH_VERBOSE", "true").lower() == "true"
        self.langgraph_max_iterations = int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "50"))
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI configuration is complete."""
        return self.openai_api_key is not None
    
    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI configuration is complete."""
        return (
            self.azure_openai_api_key is not None and
            self.azure_openai_endpoint is not None and
            self.azure_openai_deployment_name is not None
        )
    
    def get_llm_provider(self) -> str:
        """
        Determine which LLM provider is configured.
        
        Returns:
            "openai", "azure", or "none"
        """
        if self.is_openai_configured():
            return "openai"
        elif self.is_azure_openai_configured():
            return "azure"
        else:
            return "none"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        provider = self.get_llm_provider()
        
        if provider == "none":
            return False, "No LLM provider configured. Please set either OpenAI or Azure OpenAI credentials."
        
        if provider == "openai" and not self.openai_api_key:
            return False, "OPENAI_API_KEY is required but not set."
        
        if provider == "azure":
            if not self.azure_openai_api_key:
                return False, "AZURE_OPENAI_API_KEY is required but not set."
            if not self.azure_openai_endpoint:
                return False, "AZURE_OPENAI_ENDPOINT is required but not set."
            if not self.azure_openai_deployment_name:
                return False, "AZURE_OPENAI_DEPLOYMENT_NAME is required but not set."
        
        return True, None
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration (with sensitive data masked)
        """
        return {
            "env_file_loaded": self._env_file_loaded,
            "env_file_path": self._env_file_path,
            "llm_provider": self.get_llm_provider(),
            "openai_api_key": "***" if self.openai_api_key else None,
            "openai_api_base": self.openai_api_base,
            "openai_model_name": self.openai_model_name,
            "azure_openai_api_key": "***" if self.azure_openai_api_key else None,
            "azure_openai_endpoint": self.azure_openai_endpoint,
            "azure_openai_deployment_name": self.azure_openai_deployment_name,
            "azure_openai_api_version": self.azure_openai_api_version,
            "fhirsheets_working_dir": self.fhirsheets_working_dir,
            "fhirsheets_config_path": self.fhirsheets_config_path,
            "langgraph_verbose": self.langgraph_verbose,
            "langgraph_max_iterations": self.langgraph_max_iterations,
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        lines = ["LangGraphConfig:"]
        for key, value in config_dict.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def load_config(env_file: Optional[str] = None) -> LangGraphConfig:
    """
    Load configuration from environment variables.
    
    Args:
        env_file: Optional path to .env file
        
    Returns:
        LangGraphConfig instance
    """
    return LangGraphConfig(env_file=env_file)


# Global configuration instance (lazy loaded)
_config: Optional[LangGraphConfig] = None


def get_config(env_file: Optional[str] = None, reload: bool = False) -> LangGraphConfig:
    """
    Get the global configuration instance.
    
    Args:
        env_file: Optional path to .env file
        reload: If True, reload configuration even if already loaded
        
    Returns:
        LangGraphConfig instance
    """
    global _config
    
    if _config is None or reload:
        _config = load_config(env_file)
    
    return _config