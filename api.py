import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.google.calendar import GoogleCalendarTools
from agno.db.postgres import PostgresDb

load_dotenv()

vllm_base_url = os.getenv("VLLM_BASE_URL", "http://192.168.100.10:8000/v1")
vllm_api_key = os.getenv("VLLM_API_KEY", "")
vllm_model = os.getenv("VLLM_MODEL", "qwen3.8-27b")
db_url = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/cal_agent")

os.environ["VLLM_BASE_URL"] = vllm_base_url
os.environ["VLLM_API_KEY"] = vllm_api_key
os.environ["VLLM_MODEL"] = vllm_model
if vllm_api_key:
    os.environ["OPENAI_API_KEY"] = vllm_api_key
elif "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "dummy"

# Global database connection
db = PostgresDb(db_url=db_url) if db_url else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup / initialize DB if necessary
    yield
    # Cleanup

app = FastAPI(title="AI Personal Calendar Assistant API", lifespan=lifespan)

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
    timezone: str = "UTC"

class ChatResponse(BaseModel):
    session_id: str
    response: str

from datetime import datetime

def get_agent(session_id: Optional[str], timezone: str) -> Agent:
    today_str = datetime.now().strftime('%Y-%m-%d %A')
    instructions = (
        f"You are an AI Personal Calendar Assistant managing the user's Google Calendar.\n"
        f"The user's timezone is {timezone}. Today is {today_str}.\n\n"
        f"Guidelines:\n"
        f"- Before creating or moving events, CHECK AVAILABILITY to ensure there are no overlapping events.\n"
        f"- NEVER perform destructive actions (like create, reschedule, cancel) without asking the user for explicit confirmation first.\n"
        f"- Show details (title, time, guests) and say 'Shall I confirm this?' before taking action.\n"
        f"- Do NOT assume an operation succeeded without calling the API.\n"
    )

    tools = [
        GoogleCalendarTools(
            credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"),
            token_path=os.getenv("GOOGLE_TOKEN_PATH", "token.json"),
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
    ]

    model = OpenAIChat(
        id=vllm_model,
        base_url=vllm_base_url,
        api_key=vllm_api_key,
        role_map={'system': 'system', 'user': 'user', 'assistant': 'assistant', 'tool': 'tool', 'model': 'assistant'}
    )

    return Agent(
        session_id=session_id,
        model=model,
        tools=tools,
        db=db,
        instructions=[instructions],
        markdown=True,
        read_chat_history=True,
        add_history_to_context=True,
    )

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        agent = get_agent(request.session_id, request.timezone)
        # run agent
        response = agent.run(request.query)
        return ChatResponse(
            session_id=agent.session_id,
            response=response.content or "No response from model"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
