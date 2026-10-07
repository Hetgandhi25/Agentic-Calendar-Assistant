import os
os.environ["VLLM_BASE_URL"] = "http://192.168.100.10:8000/v1"
os.environ["VLLM_API_KEY"] = "llm-engineer-dev-key-change-in-prod"
os.environ["VLLM_MODEL"] = "qwen3.8-27b"

from app import build_agent

agent = build_agent("dummy_calcom_key", "", "UTC")

print("Checking availability:")
response = agent.run("What slots are free next Monday?")
print(response.content)

print("\nCreating booking:")
response = agent.run("Book a meeting for tomorrow at 2pm. My name is Test, email test@example.com")
print(response.content)
