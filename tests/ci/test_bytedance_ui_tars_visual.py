"""Tests for ByteDance UI-TARS visual capabilities integration."""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from browser_use import Agent
from browser_use.browser import BrowserSession
from browser_use.llm import ChatAnyLLM


class TestByteDanceUITARSVisual:
	"""Test ByteDance UI-TARS-1.5-7B visual capabilities through AnyLLM."""

	@pytest.fixture
	async def mock_ui_tars_llm(self):
		"""Create a mock UI-TARS LLM that simulates visual understanding."""
		mock_llm = AsyncMock(spec=ChatAnyLLM)
		
		# Mock response that demonstrates visual understanding
		mock_completion = AsyncMock()
		mock_completion.completion = """
		I can see a webpage with the following visual elements:
		- A header section with navigation menu
		- Main content area with text and images
		- Interactive buttons and form elements
		- Footer with links
		
		Based on my visual analysis, I will click on the first interactive element I can identify.
		"""
		
		mock_llm.ainvoke.return_value = mock_completion
		mock_llm.model = "bytedance/ui-tars-1.5-7b"
		mock_llm.name = "bytedance/ui-tars-1.5-7b"
		
		return mock_llm

	@pytest.fixture
	def visual_test_server(self):
		"""Create a test server with visual elements for UI-TARS to analyze."""
		server = HTTPServer(host="127.0.0.1", port=0)
		
		def visual_page_handler(request: Request):
			"""Return HTML with various visual elements."""
			html_content = """
			<!DOCTYPE html>
			<html>
			<head>
				<title>Visual Test Page</title>
				<style>
					.header { background: #333; color: white; padding: 20px; }
					.button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
					.card { border: 1px solid #ddd; padding: 20px; margin: 10px; border-radius: 8px; }
					.form-group { margin: 15px 0; }
					.text-input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; width: 200px; }
				</style>
			</head>
			<body>
				<div class="header">
					<h1>UI-TARS Visual Test</h1>
					<nav>
						<a href="#home">Home</a>
						<a href="#about">About</a>
						<a href="#contact">Contact</a>
					</nav>
				</div>
				
				<main>
					<div class="card">
						<h2>Interactive Elements</h2>
						<button class="button" id="primary-btn">Primary Action</button>
						<button class="button" id="secondary-btn">Secondary Action</button>
					</div>
					
					<div class="card">
						<h2>Form Elements</h2>
						<form id="test-form">
							<div class="form-group">
								<label for="name-input">Name:</label>
								<input type="text" id="name-input" class="text-input" placeholder="Enter your name">
							</div>
							<div class="form-group">
								<label for="email-input">Email:</label>
								<input type="email" id="email-input" class="text-input" placeholder="Enter your email">
							</div>
							<div class="form-group">
								<button type="submit" class="button">Submit Form</button>
							</div>
						</form>
					</div>
					
					<div class="card">
						<h2>Visual Content</h2>
						<p>This page contains various visual elements for UI-TARS to analyze:</p>
						<ul>
							<li>Header with navigation</li>
							<li>Interactive buttons with distinct styling</li>
							<li>Form elements with labels and inputs</li>
							<li>Card-based layout with visual hierarchy</li>
						</ul>
					</div>
				</main>
				
				<footer>
					<p>&copy; 2025 Visual Test Page</p>
				</footer>
			</body>
			</html>
			"""
			return Response(html_content, mimetype="text/html")
		
		server.expect_request("/visual-test").respond_with_handler(visual_page_handler)
		server.start()
		
		yield server
		
		server.stop()

	async def test_ui_tars_visual_element_detection(self, mock_ui_tars_llm, visual_test_server):
		"""Test that UI-TARS can detect and analyze visual elements."""
		# Configure agent with mock UI-TARS LLM
		agent = Agent(
			task="Analyze the visual elements on this page and identify interactive components",
			llm=mock_ui_tars_llm,
		)
		
		async with BrowserSession() as session:
			# Navigate to test page
			page_url = f"http://127.0.0.1:{visual_test_server.port}/visual-test"
			await session.get(page_url)
			
			# Set the browser session on the agent
			agent.browser = session
			
			# Run agent to analyze visual elements
			await agent.run(max_steps=3)
			
			# Verify that the LLM was called with visual content
			assert mock_ui_tars_llm.ainvoke.called
			
			# Check that messages contain image content (screenshots)
			call_args = mock_ui_tars_llm.ainvoke.call_args
			messages = call_args[0][0] if call_args else []
			
			# Should have messages with image content for visual analysis
			has_image_content = any(
				hasattr(msg, 'content') and 
				isinstance(msg.content, list) and 
				any(part.type == 'image_url' for part in msg.content if hasattr(part, 'type'))
				for msg in messages
			)
			
			assert has_image_content, "Expected visual content to be sent to UI-TARS model"

	async def test_ui_tars_model_configuration(self):
		"""Test that UI-TARS model is properly configured through AnyLLM."""
		# Test model configuration
		llm = ChatAnyLLM(
			model='bytedance/ui-tars-1.5-7b',
			api_key='test-key',
			api_base='https://openrouter.ai/api/v1',
			temperature=0.1,
			max_tokens=2048,
		)
		
		assert llm.model == 'bytedance/ui-tars-1.5-7b'
		assert llm.temperature == 0.1
		assert llm.max_tokens == 2048
		assert llm.api_base == 'https://openrouter.ai/api/v1'

	async def test_ui_tars_visual_task_execution(self, mock_ui_tars_llm, visual_test_server):
		"""Test UI-TARS executing visual-based tasks."""
		# Mock UI-TARS to simulate clicking on visual elements
		mock_ui_tars_llm.ainvoke.side_effect = [
			AsyncMock(completion='{"action": "click", "coordinate": [100, 200], "reasoning": "I can see a primary button that appears clickable based on its visual styling."}'),
			AsyncMock(completion='{"action": "done", "summary": "Successfully clicked on the visually identified button element."}')
		]
		
		agent = Agent(
			task="Use visual analysis to identify and click on the primary button",
			llm=mock_ui_tars_llm,
		)
		
		async with BrowserSession() as session:
			page_url = f"http://127.0.0.1:{visual_test_server.port}/visual-test"
			await session.get(page_url)
			agent.browser = session
			
			await agent.run(max_steps=2)
			
			# Verify the model was called multiple times for visual analysis
			assert mock_ui_tars_llm.ainvoke.call_count >= 2

	def test_ui_tars_environment_configuration(self):
		"""Test that environment variables are properly configured for UI-TARS."""
		# Test environment variable configuration
		with patch.dict(os.environ, {
			'ANYLLM_MODEL': 'bytedance/ui-tars-1.5-7b',
			'OPENROUTER_API_KEY': 'test-openrouter-key',
			'ANYLLM_TEMPERATURE': '0.1'
		}):
			from browser_use.config import CONFIG
			
			config = CONFIG.get_llm_config()
			
			assert config['model'] == 'bytedance/ui-tars-1.5-7b'
			assert config['api_key'] == 'test-openrouter-key'
			assert config['temperature'] == 0.1

	async def test_ui_tars_visual_form_interaction(self, mock_ui_tars_llm, visual_test_server):
		"""Test UI-TARS visual form analysis and interaction."""
		# Mock responses for form interaction
		mock_responses = [
			AsyncMock(completion='I can visually identify a form with name and email input fields. I will fill out the form.'),
			AsyncMock(completion='{"action": "type", "text": "John Doe", "reasoning": "Filling the name field based on visual analysis of the form structure."}'),
			AsyncMock(completion='{"action": "type", "text": "john@example.com", "reasoning": "Filling the email field based on visual form layout."}'),
			AsyncMock(completion='{"action": "done", "summary": "Successfully analyzed and filled the form using visual understanding."}')
		]
		mock_ui_tars_llm.ainvoke.side_effect = mock_responses
		
		agent = Agent(
			task="Visually analyze the form on this page and fill it out appropriately",
			llm=mock_ui_tars_llm,
		)
		
		async with BrowserSession() as session:
			page_url = f"http://127.0.0.1:{visual_test_server.port}/visual-test"
			await session.get(page_url)
			agent.browser = session
			
			await agent.run(max_steps=4)
			
			# Verify multiple interactions occurred
			assert mock_ui_tars_llm.ainvoke.call_count >= 3