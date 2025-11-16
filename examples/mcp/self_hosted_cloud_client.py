"""Simple client for the self-hosted Browser Use Cloud API.

This example talks to the FastAPI app in examples/api/self_hosted_cloud.py
using the same paths/headers as Browser Use Cloud v2:

- POST /api/v2/tasks
- GET  /api/v2/tasks/{task_id}

Configure via environment variables:
- SELF_HOSTED_CLOUD_URL      (default: http://localhost:8000)
- SELF_HOSTED_CLOUD_API_KEY  (required)
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict

import httpx


BASE_URL = os.getenv("SELF_HOSTED_CLOUD_URL", "http://localhost:8000")
API_KEY = os.getenv("SELF_HOSTED_CLOUD_API_KEY", "local-dev")


async def create_task(client: httpx.AsyncClient, task_text: str) -> Dict[str, Any]:
	resp = await client.post(
		f"{BASE_URL}/api/v2/tasks",
		headers={"X-Browser-Use-API-Key": API_KEY},
		json={"task": task_text, "maxSteps": 50},
	)
	resp.raise_for_status()
	return resp.json()


async def get_task(client: httpx.AsyncClient, task_id: str) -> Dict[str, Any]:
	resp = await client.get(
		f"{BASE_URL}/api/v2/tasks/{task_id}",
		headers={"X-Browser-Use-API-Key": API_KEY},
	)
	resp.raise_for_status()
	return resp.json()


async def main() -> None:
	print(f"Using self-hosted cloud at: {BASE_URL}")

	async with httpx.AsyncClient(timeout=60.0) as client:
		# 1) Create a task
		create_resp = await create_task(
			client,
			"Search for the top Hacker News post and return the title and URL.",
		)
		task_id = create_resp["id"]
		session_id = create_resp["sessionId"]

		print(f"Created task: {task_id} in session: {session_id}")

		# 2) Poll for completion
		while True:
			task_view = await get_task(client, task_id)
			status = task_view.get("status")
			print(f"Task status: {status}")

			if status in {"finished", "error"}:
				print("\nFinal task view:")
				print(task_view)
				break

			time.sleep(5)


if __name__ == "__main__":
	asyncio.run(main())
