import time
import requests
import subprocess
import threading

def run_server():
    subprocess.run([".venv\\Scripts\\python.exe", "-m", "uvicorn", "api:app", "--port", "8001"])

print("Starting server...")
t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(5)

print("Sending chat request...")
try:
    resp = requests.post(
        "http://localhost:8001/chat",
        json={"session_id": "integration_test", "query": "Hello", "timezone": "UTC"}
    )
    print("Status:", resp.status_code)
    print("Response:", resp.json())
except Exception as e:
    print("Integration test failed:", e)
