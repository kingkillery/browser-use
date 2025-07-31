from __future__ import annotations

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ChatInvokeUsage(BaseModel):
    """Usage statistics for a chat invocation."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_cached_tokens: int | None = None
    prompt_cache_creation_tokens: int | None = None
    prompt_image_tokens: int | None = None


class ChatInvokeCompletion(BaseModel, Generic[T]):
    """Output of a single chat invocation."""

    completion: T
    usage: ChatInvokeUsage | None = None
