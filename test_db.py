import os
from dotenv import load_dotenv

load_dotenv()

from api import get_agent

agent = get_agent(session_id="test_db_session", timezone="UTC")

res = agent.run("Hello, this is a test.")
print("Response:", res.content.encode('ascii', 'ignore').decode('ascii'))
