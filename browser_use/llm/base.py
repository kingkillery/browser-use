from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, overload
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion

T = TypeVar("T")


class BaseChatModel(ABC):
    """Abstract base class for all chat models."""

    model: str

    @property
    @abstractmethod
    def provider(self) -> str:
        """The provider name for this model."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the model."""
        ...

    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: None = None
    ) -> ChatInvokeCompletion[str]:
        ...

    @overload
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T]
    ) -> ChatInvokeCompletion[T]:
        ...

    @abstractmethod
    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T] | None = None
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        """
        Asynchronously invoke the chat model.

        Args:
            messages: A list of messages to send to the model.
            output_format: The desired output format. If a Pydantic model is provided,
                           the model will return a structured output.

        Returns:
            A ChatInvokeCompletion object containing the model's response.
        """
        ...