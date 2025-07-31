import asyncio
import os
import sys

# Add the current directory to the path so we can import browser_use
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent
from browser_use.llm import ChatAnyLLM

# Test with any-llm using openrouter
llm = ChatAnyLLM(
    model="openrouter/z-ai/glm-4.5-air:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.1
)

task = "Go to google.com and search for 'browser-use github'"
agent = Agent(task=task, llm=llm)

async def main():
    try:
        result = await agent.run()
        print(f"Task completed: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
