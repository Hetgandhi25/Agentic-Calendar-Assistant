import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

st.set_page_config(
    page_title="AI Personal Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Basic Streamlit UI Styling
st.markdown("""
<style>
.stApp { background-color: #0f172a; color: #e2e8f0; }
[data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
[data-testid="stChatMessage"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("### 📅 Calendar Assistant")
    timezone = st.selectbox(
        "Your timezone",
        options=["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Kolkata"],
        index=0,
    )
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

st.markdown("## AI Personal Calendar Assistant")
st.markdown("Manage your Google Calendar through natural conversation.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask anything about your schedule...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking your calendar..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={
                        "session_id": st.session_state.session_id,
                        "query": prompt,
                        "timezone": timezone
                    },
                    timeout=60
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["response"]
                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})
            except requests.exceptions.RequestException as e:
                st.error(f"Backend API error: {e}")
