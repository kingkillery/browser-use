"""Custom exceptions for LLM provider errors."""

from typing import Optional


class ModelProviderError(Exception):
    """Exception raised when a model provider encounters an error."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        model: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.model = model
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_parts = [self.message]
        if self.model:
            error_parts.append(f"Model: {self.model}")
        if self.status_code:
            error_parts.append(f"Status: {self.status_code}")
        return " | ".join(error_parts)


class ModelRateLimitError(ModelProviderError):
    """Exception raised when a model provider rate limit is exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        model: Optional[str] = None
    ):
        super().__init__(message=message, status_code=429, model=model)
