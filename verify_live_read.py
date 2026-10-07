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

agent = Agent(
    model=OpenAIChat(
        id=vllm_model, base_url=vllm_base_url, api_key=vllm_api_key,
        role_map={'system': 'system', 'user': 'user', 'assistant': 'assistant', 'tool': 'tool', 'model': 'assistant'}
    ),
    tools=[
        GoogleCalendarTools(
            credentials_path="credentials.json",
            token_path="token.json",
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
    ],
    instructions=f"Timezone is Asia/Kolkata. Today is {datetime.datetime.now().strftime('%Y-%m-%d %A')}. Keep answers concise.",
    markdown=True
)

print("\n--- 1. Testing live read-only operations (List Events) ---")
res1 = agent.run("What are my upcoming events for the next 3 days?")
print(res1.content.encode('ascii', 'ignore').decode('ascii'))

print("\n--- 2. Testing live read-only operations (Availability) ---")
res2 = agent.run("Check my availability for tomorrow.")
print(res2.content.encode('ascii', 'ignore').decode('ascii'))
