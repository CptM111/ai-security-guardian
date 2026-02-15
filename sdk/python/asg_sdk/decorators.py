"""
SDK Decorators for easy integration
"""
from functools import wraps
from typing import Callable, Any
from .exceptions import SecurityException


def protect_llm_output(func: Callable) -> Callable:
    """
    Decorator to automatically protect LLM output.
    
    Example:
        >>> from asg_sdk import asg
        >>> asg.init(api_key="your-key")
        >>> 
        >>> @asg.protect_llm_output
        >>> def generate_response(prompt: str) -> str:
        ...     return call_my_llm(prompt)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Import here to avoid circular dependency
        from .client import _global_client
        
        if _global_client is None:
            raise SecurityException("ASG client not initialized. Call asg.init() first.")
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # If result is a string, sanitize it
        if isinstance(result, str):
            response = _global_client.protect.output(
                content=result,
                context="general"
            )
            
            if response.status == "blocked":
                raise SecurityException(
                    f"Malicious content detected in output: {', '.join(response.warnings)}"
                )
            
            return response.sanitized_content
        
        return result
    
    return wrapper


def protect_llm_input(func: Callable) -> Callable:
    """
    Decorator to automatically protect LLM input (prompts).
    
    Example:
        >>> from asg_sdk import asg
        >>> asg.init(api_key="your-key")
        >>> 
        >>> @asg.protect_llm_input
        >>> def call_llm(prompt: str, model_id: str = "gpt-4") -> str:
        ...     return call_my_llm(prompt)
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Import here to avoid circular dependency
        from .client import _global_client
        
        if _global_client is None:
            raise SecurityException("ASG client not initialized. Call asg.init() first.")
        
        # Extract prompt from args or kwargs
        prompt = None
        model_id = kwargs.get("model_id", "unknown")
        
        if args and isinstance(args[0], str):
            prompt = args[0]
        elif "prompt" in kwargs:
            prompt = kwargs["prompt"]
        
        if prompt:
            # Check the prompt
            response = _global_client.protect.prompt(
                prompt=prompt,
                model_id=model_id
            )
            
            if response.status == "blocked":
                raise SecurityException(
                    f"Malicious prompt detected: {response.reason}"
                )
            
            # Use sanitized prompt if available
            if response.sanitized_prompt:
                if args and isinstance(args[0], str):
                    args = (response.sanitized_prompt,) + args[1:]
                elif "prompt" in kwargs:
                    kwargs["prompt"] = response.sanitized_prompt
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper
