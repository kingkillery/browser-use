"""
Example using ByteDance UI-TARS-1.5-7B via AnyLLM for advanced visual browser tasks.

UI-TARS is a specialized multimodal AI agent optimized for GUI-based environments,
including desktop interfaces, web browsers, mobile systems, and games.

@dev You need to set OPENROUTER_API_KEY in your environment variables.
"""

import asyncio
import os

from dotenv import load_dotenv

from browser_use import Agent
from browser_use.llm import ChatAnyLLM

load_dotenv()

# Configure AnyLLM with ByteDance UI-TARS-1.5-7B model for visual tasks
llm = ChatAnyLLM(
	model='bytedance/ui-tars-1.5-7b',
	api_key=os.getenv('OPENROUTER_API_KEY'),
	api_base='https://openrouter.ai/api/v1',
	temperature=0.1,  # Lower temperature for more precise visual understanding
	max_tokens=2048,  # Higher token limit for detailed visual descriptions
)

# Example task that leverages UI-TARS's visual capabilities
agent = Agent(
	task=(
		"Navigate to https://example.com and perform a detailed visual analysis. "
		"Identify all interactive elements, describe the visual layout, "
		"click on any links you find, and provide a comprehensive report "
		"of the visual structure and content of each page you visit."
	),
	llm=llm,
)


async def main():
	"""Run the ByteDance UI-TARS visual browser agent."""
	print("🎯 Starting ByteDance UI-TARS-1.5-7B Visual Browser Agent")
	print("🔍 This model is optimized for visual UI understanding and interaction")
	print("=" * 60)
	
	await agent.run(max_steps=15)
	
	print("=" * 60)
	print("✅ Visual analysis complete!")
	input('Press Enter to continue...')


async def visual_form_filling_example():
	"""Example of using UI-TARS for complex form interaction."""
	form_agent = Agent(
		task=(
			"Go to a demo form website (like https://httpbin.org/forms/post) "
			"and demonstrate advanced form filling capabilities. "
			"Analyze the form structure visually, identify all input fields, "
			"fill them with appropriate test data, and submit the form. "
			"Provide detailed feedback on each step of the interaction."
		),
		llm=llm,
	)
	
	print("🎯 Starting Advanced Form Filling Demo")
	print("🤖 UI-TARS will visually analyze and interact with forms")
	print("=" * 60)
	
	await form_agent.run(max_steps=20)


async def ecommerce_navigation_example():
	"""Example of using UI-TARS for e-commerce site navigation."""
	ecommerce_agent = Agent(
		task=(
			"Navigate to an e-commerce demo site and perform product research. "
			"Visually identify product categories, browse different sections, "
			"analyze product listings, and provide insights on the site's "
			"visual design and user experience. Focus on understanding "
			"the visual hierarchy and interaction patterns."
		),
		llm=llm,
	)
	
	print("🎯 Starting E-commerce Visual Navigation Demo")
	print("🛒 UI-TARS will analyze e-commerce interfaces visually")
	print("=" * 60)
	
	await ecommerce_agent.run(max_steps=25)


if __name__ == '__main__':
	# Run the main visual analysis example
	asyncio.run(main())
	
	# Uncomment to run additional examples:
	# asyncio.run(visual_form_filling_example())
	# asyncio.run(ecommerce_navigation_example())