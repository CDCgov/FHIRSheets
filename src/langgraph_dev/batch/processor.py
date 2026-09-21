"""
Batch Processor for FHIRSheets AI Agent

This module provides functionality for automated sequential prompting,
allowing the agent to process multiple messages in series without manual intervention.
"""

from typing import List, Dict, Any, Optional, Callable
import logging
import json
from pathlib import Path
from datetime import datetime

from ..agent import FHIRSheetsAIAgent, create_agent
from ..config import LangGraphConfig
from .config import BatchProcessorConfig
from ..tools.fhirsheets_xlsx_tool import WorkbookManager

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Batch processor for automated sequential prompting.
    
    This class allows you to queue multiple prompts and process them
    sequentially through the AI agent, with optional callbacks and
    result tracking.
    """
    
    def __init__(
        self,
        agent: Optional[FHIRSheetsAIAgent] = None,
        agent_config: Optional[LangGraphConfig] = None,
        batch_config: Optional[BatchProcessorConfig] = None,
        working_dir: Optional[str] = None
    ):
        """
        Initialize the batch processor.
        
        Args:
            agent: Optional pre-configured agent. If not provided, creates a new one.
            agent_config: Configuration for the FHIRSheets AI Agent
            batch_config: Configuration for batch processing behavior
            working_dir: Working directory for Excel files (overrides agent_config if provided)
        """
        # Initialize batch configuration
        self.batch_config = batch_config or BatchProcessorConfig()
        
        # Create or use provided agent
        if agent:
            self.agent = agent
        else:
            self.agent = create_agent(
                working_dir=working_dir,
                verbose=self.batch_config.verbose,
                config=agent_config
            )
        
        # Set up results directory
        if self.batch_config.results_dir:
            self.results_dir = Path(self.batch_config.results_dir)
        else:
            self.results_dir = Path(self.agent.working_dir) / "batch_results"
        
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Track processing state
        self.prompts: List[str] = []
        self.results: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.thread_id: str = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.batch_config.verbose:
            print(f"Batch Processor initialized")
            print(f"  Thread ID: {self.thread_id}")
            print(f"  Results Directory: {self.results_dir}")
    
    def add_prompt(self, prompt: str) -> None:
        """
        Add a prompt to the processing queue.
        
        Args:
            prompt: The prompt text to add
        """
        self.prompts.append(prompt)
        if self.batch_config.verbose:
            print(f"Added prompt #{len(self.prompts)}: {prompt[:50]}...")
    
    def add_prompts(self, prompts: List[str]) -> None:
        """
        Add multiple prompts to the processing queue.
        
        Args:
            prompts: List of prompt texts to add
        """
        for prompt in prompts:
            self.add_prompt(prompt)
    
    def load_prompts_from_file(self, filepath: str, format: str = "txt") -> None:
        """
        Load prompts from a file.
        
        Args:
            filepath: Path to the file containing prompts
            format: File format - "txt" (one prompt per line), "json" (array of strings),
                   or "jsonl" (one JSON object per line with "prompt" key)
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Prompts file not found: {filepath}")
        
        if format == "txt":
            with open(path, 'r') as f:
                prompts = [line.strip() for line in f if line.strip()]
        elif format == "json":
            with open(path, 'r') as f:
                prompts = json.load(f)
                if not isinstance(prompts, list):
                    raise ValueError("JSON file must contain an array of strings")
        elif format == "jsonl":
            prompts = []
            with open(path, 'r') as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        prompts.append(obj.get("prompt", ""))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.add_prompts(prompts)
        
        if self.batch_config.verbose:
            print(f"Loaded {len(prompts)} prompts from {filepath}")
    
    def _is_context_window_error(self, error: Exception) -> bool:
        """
        Check if an error is a context window exceeded error.
        
        Args:
            error: The exception to check
            
        Returns:
            True if the error is related to context window limits
        """
        error_str = str(error).lower()
        return any(keyword.lower() in error_str for keyword in self.batch_config.context_window_error_keywords)
    
    def _clear_context(self) -> None:
        """
        Clear the conversation context by creating a new thread ID.
        This effectively starts a fresh conversation with no history.
        """
        old_thread_id = self.thread_id
        self.thread_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self._message_count = 0  # Reset message count
        
        if self.batch_config.verbose:
            print(f"\n🔄 Context cleared: {old_thread_id} → {self.thread_id}")
    
    def process_all(
        self,
        on_prompt_start: Optional[Callable[[int, str], None]] = None,
        on_prompt_complete: Optional[Callable[[int, Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[int, Exception], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all prompts in the queue sequentially.
        
        Args:
            on_prompt_start: Callback called before processing each prompt (index, prompt)
            on_prompt_complete: Callback called after processing each prompt (index, result)
            on_error: Callback called when an error occurs (index, exception)
            
        Returns:
            List of results for each prompt
        """
        self.results = []
        
        if self.batch_config.verbose:
            print(f"\n{'='*60}")
            print(f"Starting batch processing of {len(self.prompts)} prompts")
            print(f"{'='*60}\n")
        
        for idx, prompt in enumerate(self.prompts):
            self.current_index = idx
            retry_count = 0
            success = False
            
            while not success and retry_count <= self.batch_config.max_retries:
                try:
                    # Call start callback (only on first attempt)
                    if retry_count == 0 and on_prompt_start:
                        on_prompt_start(idx, prompt)
                    
                    if self.batch_config.verbose:
                        print(f"\n{'='*60}")
                        if retry_count == 0:
                            print(f"Processing prompt {idx + 1}/{len(self.prompts)}")
                        else:
                            print(f"Retrying prompt {idx + 1}/{len(self.prompts)} (attempt {retry_count + 1}/{self.batch_config.max_retries + 1})")
                        print(f"{'='*60}")
                    
                    # Process the prompt
                    result = self.agent.run(
                        user_input=prompt,
                        thread_id=self.thread_id,
                        stream=self.batch_config.stream
                    )
                    
                    # Add metadata to result
                    result["prompt_index"] = idx
                    result["prompt"] = prompt
                    result["timestamp"] = datetime.now().isoformat()
                    result["retry_count"] = retry_count
                    
                    # Handle message tracking based on thread reset configuration
                    all_messages = result.get("messages", [])
                    
                    if self.batch_config.reset_thread_per_message:
                        # When resetting thread per message, each message starts fresh
                        # so we keep all messages from this iteration
                        result["messages"] = all_messages
                    else:
                        # When using the same thread_id, messages accumulate in the agent's state
                        # We need to track the total count and only keep the new ones
                        if idx == 0 and retry_count == 0:
                            # First prompt: keep all messages (system, user, AI response, tool messages)
                            result["messages"] = all_messages
                            # Track how many messages we have after first iteration
                            self._message_count = len(all_messages)
                        else:
                            # Subsequent prompts: only keep messages added in this iteration
                            # Skip the accumulated history from previous iterations
                            result["messages"] = all_messages[self._message_count:]
                            # Update the count for next iteration
                            self._message_count = len(all_messages)
                    
                    self.results.append(result)
                    success = True
                    
                    # Call complete callback
                    if on_prompt_complete:
                        on_prompt_complete(idx, result)
                    
                    if self.batch_config.verbose:
                        print(f"\n✓ Completed prompt {idx + 1}/{len(self.prompts)}")
                    
                    # Reset thread_id after each message if configured
                    if self.batch_config.reset_thread_per_message or self.batch_config.reset_thread_per_message:
                        self._clear_context()
                    
                except Exception as e:
                    # Check if this is a context window error and we should retry
                    is_context_error = self._is_context_window_error(e)
                    should_retry = (
                        is_context_error and 
                        self.batch_config.clear_context_on_error and 
                        retry_count < self.batch_config.max_retries
                    )
                    
                    if should_retry:
                        retry_count += 1
                        if self.batch_config.verbose:
                            print(f"\n⚠️  Context window error detected on prompt {idx + 1}/{len(self.prompts)}")
                            print(f"   Error: {str(e)[:200]}...")
                        
                        # Clear context and retry
                        self._clear_context()
                        continue
                    else:
                        # Either not a context error, retries disabled, or max retries reached
                        error_result = {
                            "prompt_index": idx,
                            "prompt": prompt,
                            "success": False,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                            "retry_count": retry_count,
                            "is_context_window_error": is_context_error
                        }
                        self.results.append(error_result)
                        
                        # Call error callback
                        if on_error:
                            on_error(idx, e)
                        
                        if self.batch_config.verbose:
                            print(f"\n✗ Error processing prompt {idx + 1}/{len(self.prompts)}: {e}")
                            if is_context_error and retry_count >= self.batch_config.max_retries:
                                print(f"   Max retries ({self.batch_config.max_retries}) reached")
                        
                        if self.batch_config.stop_on_error:
                            if self.batch_config.verbose:
                                print("\nStopping batch processing due to error")
                            break
                        
                        success = True  # Exit retry loop
            
            # If stop_on_error and we had an error, break outer loop
            if self.batch_config.stop_on_error and not self.results[-1].get('success', True):
                break
        
        # Auto-save results if enabled
        if self.batch_config.auto_save_results:
            self.save_results()
        
        if self.batch_config.verbose:
            print(f"\n{'='*60}")
            print(f"Batch processing complete")
            print(f"  Total prompts: {len(self.prompts)}")
            print(f"  Successful: {sum(1 for r in self.results if r.get('success', True))}")
            print(f"  Failed: {sum(1 for r in self.results if not r.get('success', True))}")
            context_errors = sum(1 for r in self.results if r.get('is_context_window_error', False))
            if context_errors > 0:
                print(f"  Context window errors: {context_errors}")
            print(f"{'='*60}\n")
        
        # Close any open workbook after batch processing
        try:
            if WorkbookManager.is_open():
                if self.batch_config.verbose:
                    print("Closing workbook after batch processing...")
                close_result = WorkbookManager.close_workbook(save=True)
                if self.batch_config.verbose:
                    print(f"Workbook closed: {close_result.get('message', 'Done')}")
        except Exception as e:
            if self.batch_config.verbose:
                print(f"Warning: Error closing workbook: {e}")
        
        return self.results
    
    def save_results(self, filepath: Optional[str] = None) -> str:
        """
        Save processing results to a JSON file.
        
        Args:
            filepath: Optional custom filepath. If not provided, uses auto-generated name.
            
        Returns:
            Path to the saved file
        """
        if filepath:
            output_path = Path(filepath)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.results_dir / f"batch_results_{timestamp}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "thread_id": self.thread_id,
            "timestamp": datetime.now().isoformat(),
            "total_prompts": len(self.prompts),
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        if self.batch_config.verbose:
            print(f"Results saved to: {output_path}")
        
        return str(output_path)
    
    def clear(self) -> None:
        """Clear all prompts and results."""
        self.prompts = []
        self.results = []
        self.current_index = 0
        
        if self.batch_config.verbose:
            print("Batch processor cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the batch processing results.
        
        Returns:
            Dictionary containing summary statistics
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        failed = total - successful
        
        return {
            "thread_id": self.thread_id,
            "total_prompts": len(self.prompts),
            "processed": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "results": self.results
        }


def create_batch_processor(
    agent_config: Optional[LangGraphConfig] = None,
    batch_config: Optional[BatchProcessorConfig] = None,
    working_dir: Optional[str] = None
) -> BatchProcessor:
    """
    Factory function to create a batch processor.
    
    Args:
        agent_config: Configuration for the FHIRSheets AI Agent
        batch_config: Configuration for batch processing behavior
        working_dir: Working directory for Excel files
        
    Returns:
        Configured BatchProcessor instance
    """
    return BatchProcessor(
        agent_config=agent_config,
        batch_config=batch_config,
        working_dir=working_dir
    )