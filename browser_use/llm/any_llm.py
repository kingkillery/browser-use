from dataclasses import dataclass
from typing import Any, TypeVar, overload

from any_llm import acompletion
from pydantic import BaseModel

from browser_use.llm.base import BaseChatModel
from browser_use.llm.exceptions import ModelProviderError
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage

T = TypeVar("T", bound=BaseModel)


@dataclass
class ChatAnyLLM(BaseChatModel):
    """
    A wrapper around any-llm to support multiple LLM providers.
    """

    model: str
    api_key: str | None = None
    api_base: str | None = None
    temperature: float = 0.0
    max_tokens: int = 1024
    top_p: float = 1.0

    @property
    def provider(self) -> str:
        return self.model.split('/')[0]

    @property
    def name(self) -> str:
        return str(self.model)

    def _get_usage(self, response: Any) -> ChatInvokeUsage | None:
        # Implement usage extraction based on any-llm's response format
        if hasattr(response, 'usage'):
            usage = response.usage
            return ChatInvokeUsage(
                prompt_tokens=getattr(usage, 'prompt_tokens', 0),
                completion_tokens=getattr(usage, 'completion_tokens', 0),
                total_tokens=getattr(usage, 'total_tokens', 0),
            )
        return None

    @overload
    async def ainvoke(self, messages: list[BaseMessage], output_format: None = None) -> ChatInvokeCompletion[str]: ...

    @overload
    async def ainvoke(self, messages: list[BaseMessage], output_format: type[T]) -> ChatInvokeCompletion[T]: ...

    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T] | None = None
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        message_dicts = [msg.model_dump() for msg in messages]

        try:
            # Use any-llm's acompletion function directly
            response = await acompletion(
                model=self.model,
                messages=message_dicts,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                api_key=self.api_key,
                api_base=self.api_base,
            )

            completion = response.choices[0].message.content or ""
            if output_format:
                return ChatInvokeCompletion(
                    completion=output_format.model_validate_json(completion),
                    usage=self._get_usage(response),
                )
            else:
                return ChatInvokeCompletion(
                    completion=completion,
                    usage=self._get_usage(response),
                )

        except Exception as e:
            raise ModelProviderError(message=str(e), model=self.name) from e
