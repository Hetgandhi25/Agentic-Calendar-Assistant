import os
from agno.tools.google.calendar import GoogleCalendarTools

tools = GoogleCalendarTools(
    credentials_path="credentials.json",
    token_path="token.json",
    scopes=["https://www.googleapis.com/auth/calendar"]
)
print("Triggering OAuth flow. Check your browser...")
tools.list_events()
print("OAuth configuration successful! token.json created.")
