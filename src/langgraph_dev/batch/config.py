"""
Configuration for Batch Processor.

This module provides configuration specific to batch processing operations.
"""

from typing import Optional
from pathlib import Path


class BatchProcessorConfig:
    """Configuration class for batch processing operations."""
    
    def __init__(
        self,
        verbose: bool = True,
        auto_save_results: bool = True,
        results_dir: Optional[str] = None,
        stop_on_error: bool = False,
        stream: bool = True,
        clear_context_on_error: bool = True,
        max_retries: int = 3,
        context_window_error_keywords: Optional[list] = None,
        reset_thread_per_message: bool = True
    ):
        """
        Initialize batch processor configuration.
        
        Args:
            verbose: Enable verbose logging during batch processing
            auto_save_results: Automatically save results to JSON after processing
            results_dir: Directory to save results (defaults to working_dir/batch_results)
            stop_on_error: If True, stop processing on first error
            stream: Whether to stream responses during processing
            clear_context_on_error: If True, clear context and retry on context window errors
            max_retries: Maximum number of retries for context window errors
            context_window_error_keywords: Keywords to detect context window errors
            reset_thread_per_message: If True, reset thread_id after each message to clear context
        """
        self.verbose = verbose
        self.auto_save_results = auto_save_results
        self.results_dir = results_dir
        self.stop_on_error = stop_on_error
        self.stream = stream
        self.clear_context_on_error = clear_context_on_error
        self.max_retries = max_retries
        self.reset_thread_per_message = reset_thread_per_message
        
        # Default keywords to detect context window exceeded errors
        if context_window_error_keywords is None:
            self.context_window_error_keywords = [
                "context window",
                "context_window",
                "ContextWindowExceededError",
                "Input is too long",
                "maximum context length",
                "token limit"
            ]
        else:
            self.context_window_error_keywords = context_window_error_keywords
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "verbose": self.verbose,
            "auto_save_results": self.auto_save_results,
            "results_dir": self.results_dir,
            "stop_on_error": self.stop_on_error,
            "stream": self.stream,
            "clear_context_on_error": self.clear_context_on_error,
            "max_retries": self.max_retries,
            "context_window_error_keywords": self.context_window_error_keywords,
            "reset_thread_per_message": self.reset_thread_per_message,
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        lines = ["BatchProcessorConfig:"]
        for key, value in config_dict.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)