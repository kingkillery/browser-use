import os
import pytest
from pydantic import BaseModel
from browser_use.llm import ChatAnyLLM, BaseMessage, UserMessage, SystemMessage

class CapitalResponse(BaseModel):
    country: str
    capital: str

@pytest.mark.asyncio
async def test_any_llm_openrouter():
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    llm = ChatAnyLLM(
        model="openrouter/z-ai/glm-4.5-air:free",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    messages: list[BaseMessage] = [
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="What is the capital of France?"),
    ]

    response = await llm.ainvoke(messages)
    assert isinstance(response.completion, str)
    assert "paris" in response.completion.lower()
