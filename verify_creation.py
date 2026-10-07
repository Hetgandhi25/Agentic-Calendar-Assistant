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
    instructions=f"Timezone is Asia/Kolkata. Today is {datetime.datetime.now().strftime('%Y-%m-%d %A')}. Guidelines: NEVER perform destructive actions (create, delete, update) without explicit confirmation first.",
)

print("\n--- Testing Safety Rules (Event Creation Draft) ---")
res = agent.run("Create a test meeting for tomorrow at 2 PM.")
print(res.content.encode('ascii', 'ignore').decode('ascii'))
