"""
Example using OpenRouter with GLM-4.5-Air model for browser-use.

@dev You need to set OPENROUTER_API_KEY in your environment variables.
"""

import asyncio
import os

from dotenv import load_dotenv

from browser_use import Agent
from browser_use.llm import ChatOpenRouter

load_dotenv()

# Configure OpenRouter LLM with GLM-4.5-Air model
llm = ChatOpenRouter(
    model='z-ai/glm-4.5-air',
    api_key=os.getenv('OPENROUTER_API_KEY'),
    temperature=0.7,
)

agent = Agent(
    task='Go to example.com and tell me what you see on the page',
    llm=llm,
)


async def main():
    await agent.run(max_steps=10)
    input('Press Enter to continue...')


if __name__ == '__main__':
    asyncio.run(main())
