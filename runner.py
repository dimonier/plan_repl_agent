import requests
import time
import sys
import argparse
from typing import Optional
from pathlib import Path

BASE_URL = "http://localhost:8000"


def run_task(task: str) -> dict:
    """Run a task on the agent server."""
    response = requests.post(f"{BASE_URL}/run", json={"task": task})
    response.raise_for_status()
    return response.json()


def list_tasks() -> dict:
    """List all tasks from the agent server."""
    response = requests.get(f"{BASE_URL}/tasks")
    response.raise_for_status()
    return response.json()


def reset() -> dict:
    """Reset the agent server."""
    response = requests.get(f"{BASE_URL}/reset")
    response.raise_for_status()
    return response.json()


task = """

create doc.txt in CWD

""".strip()

run_task(task)
time.sleep(0.5)
print(list_tasks())