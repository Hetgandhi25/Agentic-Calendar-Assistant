import os
import pytest
from unittest.mock import MagicMock, patch

# Set env vars for tests BEFORE importing api
os.environ["VLLM_BASE_URL"] = "http://192.168.100.10:8000/v1"
os.environ["VLLM_API_KEY"] = "llm-engineer-dev-key-change-in-prod"
os.environ["VLLM_MODEL"] = "qwen3.8-27b"
os.environ["POSTGRES_URL"] = "" # Disable DB for tests by passing empty

patch("agno.tools.google.calendar.GoogleCalendarTools.__init__", return_value=None).start()
patch("api.GoogleCalendarTools").start()

from api import get_agent
from agno.tools import Function

def get_events():
    """List events"""
    return "['Meeting with John at 2pm']"

def create_event(title: str, time: str):
    """Create an event"""
    return "Event created successfully"

def find_available_slots(date: str):
    """Find available slots for a date"""
    return "Available slots: 10:00 AM, 1:00 PM"

def update_event(id: str, time: str):
    """Update event"""
    return "Event updated successfully"

def delete_event(id: str):
    """Delete event"""
    return "Event deleted successfully"

def test_agent_workflows():
    agent = get_agent(session_id="test_session", timezone="UTC")

    
    agent.tools = [
        Function(name="get_events", func=get_events),
        Function(name="create_event", func=create_event),
        Function(name="find_available_slots", func=find_available_slots),
        Function(name="update_event", func=update_event),
        Function(name="delete_event", func=delete_event),
    ]
    
    print("Testing availability check...")
    res = agent.run("Check my availability for tomorrow.")
    print("Response:", res.content.encode('ascii', 'ignore').decode('ascii'))
    assert "10:00" in res.content or "1:00" in res.content or "available" in res.content.lower()

    print("Testing event listing...")
    res = agent.run("What are my upcoming events?")
    print("Response:", res.content.encode('ascii', 'ignore').decode('ascii'))
    assert "John" in res.content or "2pm" in res.content or "meeting" in res.content.lower()
    
    print("Testing confirmation requirement for creation...")
    res = agent.run("Create a meeting for 3pm tomorrow.")
    print("Response:", res.content.encode('ascii', 'ignore').decode('ascii'))
    # The agent should ask for confirmation, NOT directly create it
    assert "confirm" in res.content.lower() or "shall i" in res.content.lower()

if __name__ == "__main__":
    test_agent_workflows()
    print("All basic workflow logic verified!")
