# 📅 AI Personal Calendar Assistant

An enterprise-grade, autonomous AI scheduling assistant powered by **Local vLLM (Qwen 3.8-27B)**, **FastAPI**, **Agno**, and **Google Calendar OAuth 2.0**. This agent allows users to manage their schedules securely using natural language, featuring zero API token costs, private inference, stateful PostgreSQL memory, and strict human-in-the-loop safety constraints.

---

## 🏗️ Architecture

This project is built using a decoupled microservice architecture, allowing the AI orchestration to scale independently of the user interface.

```mermaid
graph TD
    User(["👤 User"]) -->|"Natural Language"| UI(["🖥️ Streamlit Frontend"])
    UI -->|"HTTP POST"| API(["⚡ FastAPI Backend"])
    
    subgraph "Agent Orchestration"
        API --> Agent(["🤖 Agno Agent"])
        Agent <-->|"Read/Write History"| DB[("🐘 PostgreSQL")]
        Agent <-->|"Context & Tool Calls"| LLM(["🧠 Local vLLM Qwen 27B"])
    end
    
    subgraph "External Integrations"
        Agent -->|"JSON Payloads"| Tools(["🛠️ Google Calendar Tools"])
        Tools <-->|"OAuth 2.0"| GCal(["📅 Google Calendar API"])
    end

    style User fill:#f9f,stroke:#333,stroke-width:2px
    style LLM fill:#ff9900,stroke:#333,stroke-width:2px
    style GCal fill:#4285F4,stroke:#333,stroke-width:2px
```

### ⚙️ Execution Flow (Sequence Diagram)
This diagram explains how a typical request (e.g., "Schedule a meeting for tomorrow") is processed safely.

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI Backend
    participant Agent as Agno Agent
    participant LLM as vLLM (Qwen)
    participant GCal as Google Calendar API

    User->>UI: "Schedule a meeting for tomorrow at 2 PM"
    UI->>API: POST /chat
    API->>Agent: Run Agent with prompt
    Agent->>LLM: Request Intent Analysis
    LLM-->>Agent: Call Tool: find_available_slots()
    Agent->>GCal: Check Availability for tomorrow
    GCal-->>Agent: Return open slots
    Agent->>LLM: Feed slots back to LLM
    LLM-->>Agent: Generate Draft & Ask Confirmation
    Agent-->>API: "I found a slot. Shall I confirm?"
    API-->>UI: Return Response
    UI-->>User: Display Draft
    User->>UI: "Yes, confirm it."
    UI->>API: POST /chat
    API->>Agent: Run Agent with confirmation
    Agent->>LLM: Request Action
    LLM-->>Agent: Call Tool: create_event()
    Agent->>GCal: Create Event
    GCal-->>Agent: Return Event ID
    Agent->>LLM: Feed Success back to LLM
    LLM-->>Agent: Generate Final Success Message
    Agent-->>API: "Event created successfully!"
    API-->>UI: Return Final Message
    UI-->>User: Display Confirmation
```

### 🧠 Agent Decision Logic (Flowchart)
This flowchart demonstrates the safety guardrails and internal logic the agent follows before modifying your calendar.

```mermaid
flowchart TD
    Start(["💬 User Input"]) --> Parse["🤖 Agent Parses Intent"]
    Parse --> IsDestructive{"Is action destructive?<br/>(Create/Move/Delete)"}
    
    IsDestructive -- Yes --> HasConfirmed{"Has user explicitly<br/>confirmed?"}
    HasConfirmed -- No --> Draft["📝 Draft action & Ask for Confirmation"]
    Draft --> End(["✅ Return Response to User"])
    
    HasConfirmed -- Yes --> CallTool["🚀 Execute Tool Call via Google API"]
    IsDestructive -- No --> CallTool
    
    CallTool --> Success{"API Success?"}
    Success -- Yes --> ReturnSuccess["🎉 Format Success Message"]
    Success -- No --> ReturnError["⚠️ Format Error & Suggest Fix"]
    
    ReturnSuccess --> End
    ReturnError --> End
```

### Core Components
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **LLM Inference** | `vLLM` (Local DGX) | Runs Qwen 27B locally ensuring 100% data privacy and 0 API costs. |
| **Agent Framework** | `Agno` | Orchestrates tool-calling, manages prompt injection, and binds memory. |
| **Backend API** | `FastAPI` | Exposes the agent as a scalable REST endpoint (`/chat`). |
| **Frontend** | `Streamlit` | Provides an intuitive conversational UI for the user. |
| **Session Memory** | `PostgreSQL` | Persists conversation history across sessions via SQLAlchemy. |
| **Integration** | `Google OAuth 2.0` | Securely reads and mutates the user's real calendar. |

---

## ✨ Features

- **🗣️ Natural Language Scheduling:** Ask the agent to find time, schedule meetings, or reschedule events without clicking through calendars.
- **🛡️ Safety-First Execution:** The agent is hard-prompted to draft destructive actions (create, delete, reschedule) and halt for explicit user confirmation before ever modifying the live calendar.
- **🔄 Contextual Memory:** Remembers entities (like "the meeting") across multiple messages to execute complex workflows.
- **⏱️ Dynamic Timezone & Date Context:** Automatically resolves relative dates ("tomorrow", "next Friday") based on real-time injection.
- **🔒 100% Private:** LLM inference runs strictly on local hardware. No calendar data is sent to OpenAI, Anthropic, or Gemini.

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.12+**
2. **PostgreSQL** instance running locally.
3. **vLLM** server running an OpenAI-compatible model (e.g., Qwen 27B) that supports Tool Calling.
4. **Google Cloud Console Project** with the Google Calendar API enabled and Desktop OAuth 2.0 credentials (`credentials.json`).

### 1. Environment Setup

Clone the repository and set up your `.env` file:
```bash
# Rename the example file
cp .env.example .env
```

Ensure your `.env` has the correct configurations:
```ini
# Local vLLM Server
VLLM_BASE_URL=http://<YOUR_IP>:8000/v1
VLLM_API_KEY=your_key
VLLM_MODEL=qwen3.8-27b

# PostgreSQL (Make sure to URL-encode special characters in the password!)
POSTGRES_URL=postgresql+psycopg2://postgres:your%40password@localhost:5432/cal_agent
```

### 2. Google OAuth Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Calendar API**.
3. Create an **OAuth 2.0 Client ID** (Desktop Application type).
4. Download the JSON file and save it as `credentials.json` in the root of this project.

### 3. Running the Application

You will need two terminal windows to run the decoupled architecture.

**Terminal 1: Start the FastAPI Backend**
```bash
uv run uvicorn api:app --reload --port 8000
```
*(Note: On the very first request to the Calendar, the backend will trigger a browser pop-up to authenticate your Google Account and generate a `token.json` file).*

**Terminal 2: Start the Streamlit Frontend**
```bash
uv run streamlit run app.py
```

---

## 🧪 Testing Queries

To test the system, try chaining these queries in the Streamlit UI:
1. **Read:** *"What do I have on my calendar for the next 3 days?"*
2. **Find Availability:** *"Check my availability for tomorrow afternoon."*
3. **Draft Event:** *"Draft a 45-minute sync with the design team for tomorrow at 2 PM."*
4. **Confirm (Safety):** *"Yes, confirm and schedule it."*
5. **Contextual Reschedule:** *"Actually, move that sync to Friday at 3 PM instead."*
6. **Teardown:** *"Cancel the design team sync entirely."*

---
*Built with Agentic AI principles.*
