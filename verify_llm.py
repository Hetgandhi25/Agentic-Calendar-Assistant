import os
import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Function

load_dotenv()
vllm_base_url = os.getenv("VLLM_BASE_URL", "http://192.168.100.10:8000/v1")
vllm_api_key = os.getenv("VLLM_API_KEY", "")
vllm_model = os.getenv("VLLM_MODEL", "qwen3.8-27b")
os.environ["OPENAI_API_KEY"] = vllm_api_key

print("1. Checking available models from vLLM...")
try:
    resp = requests.get(f"{vllm_base_url}/models", headers={"Authorization": f"Bearer {vllm_api_key}"}, timeout=5)
    resp.raise_for_status()
    models = [m['id'] for m in resp.json().get('data', [])]
    print(f"Available models: {models}")
    if vllm_model not in models:
        print(f"WARNING: Configured model {vllm_model} not in available models.")
    else:
        print(f"Model {vllm_model} is available.")
except Exception as e:
    print(f"Failed to fetch models: {e}")

print("\n2. Testing normal response via Agent...")
agent = Agent(
    model=OpenAIChat(
        id=vllm_model, base_url=vllm_base_url, api_key=vllm_api_key,
        role_map={'system': 'system', 'user': 'user', 'assistant': 'assistant', 'tool': 'tool', 'model': 'assistant'}
    ),
    instructions=["You are a helpful assistant. Keep answers under 10 words."]
)
try:
    res = agent.run("What is 2+2?")
    print("Normal Response:", res.content)
except Exception as e:
    print("Agent run failed:", e)

print("\n3. Testing tool call via Agent...")
def get_current_weather(location: str):
    """Get the current weather in a given location"""
    return f"The weather in {location} is 72F and sunny."

agent_tool = Agent(
    model=OpenAIChat(
        id=vllm_model, base_url=vllm_base_url, api_key=vllm_api_key,
        role_map={'system': 'system', 'user': 'user', 'assistant': 'assistant', 'tool': 'tool', 'model': 'assistant'}
    ),
    tools=[Function(name="get_current_weather", func=get_current_weather)],
)
try:
    res = agent_tool.run("What is the weather in San Francisco?")
    print("Tool Call Response:", res.content)
except Exception as e:
    print("Agent tool run failed:", e)
