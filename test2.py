import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.calcom import CalComTools

model = OpenAIChat(
    id="qwen3.8-27b",
    base_url="http://192.168.100.10:8000/v1",
    api_key="llm-engineer-dev-key-change-in-prod",
)

calcom_tools = CalComTools(
    api_key="dummy_calcom_api_key",
    user_timezone="UTC",
)

agent = Agent(
    name="Test Agent",
    model=model,
    tools=[calcom_tools],
)

response = agent.run("What slots are free next Monday?")
print(response.content)
