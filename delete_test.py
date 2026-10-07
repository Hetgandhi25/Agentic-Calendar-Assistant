import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.google.calendar import GoogleCalendarTools
import datetime

load_dotenv()
vllm_base_url = os.getenv("VLLM_BASE_URL", "http://192.168.100.10:8000/v1")
vllm_api_key = os.getenv("VLLM_API_KEY", "")
vllm_model = os.getenv("VLLM_MODEL", "qwen3.8-27b")
os.environ["OPENAI_API_KEY"] = vllm_api_key

tools = GoogleCalendarTools(
    credentials_path="credentials.json",
    token_path="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"]
)
res = tools.delete_event(event_id='q5nklljd7190toagp2fqidte4k')
print("Event deleted:", res)
