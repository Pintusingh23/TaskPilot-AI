# TaskPilot AI — Full-Stack Personal AI Productivity Assistant

TaskPilot AI is an enterprise-grade personal productivity assistant powered by **Groq LLM (`openai/gpt-oss-20b`)**, **FastAPI**, **PostgreSQL (Supabase)**, and a modern **React + Tailwind CSS** dashboard.

It provides natural-language task management, conversational AI with database-backed memory, Google Calendar scheduling, Gmail inbox reading and email dispatching with two-phase safety confirmation, live web search via Tavily, and calculation tools.

---

## 🌟 Key Features

* **AI Agent with Multi-Step Tool Calling**:
  * Groq-powered conversational engine (`openai/gpt-oss-20b`).
  * Automated tool calling for tasks, calendar, emails, web search, and math calculations.
  * Explicit user confirmation guardrails before executing external write actions (sending emails, scheduling calendar events, and deleting tasks).
* **Supabase PostgreSQL & SQLAlchemy ORM**:
  * Persistent storage for Users, Conversations, Chat Messages, and Tasks.
  * Relational data integrity with cascading deletes and indexing.
  * Automatic fallback to local SQLite for offline development if the remote database is unreachable.
  * Schema migrations managed via **Alembic**.
* **Secure Authentication**:
  * JWT access tokens with bcrypt password hashing.
  * Complete user-level data isolation for tasks and conversations.
* **Full Task Management System**:
  * CRUD operations with priority levels (`low`, `medium`, `high`) and statuses (`pending`, `in_progress`, `completed`).
  * Due dates, keyword search, and multi-criteria filtering.
  * Natural language task operations via the AI assistant.
* **Modern React SaaS Dashboard**:
  * Built with **React 18**, **Vite**, **Tailwind CSS**, and **Lucide React**.
  * Responsive layout with dark/light mode toggle.
  * Kanban board and list view for tasks.
  * Interactive AI chat assistant with tool execution badges and action preview confirmation cards.
  * Google Calendar events viewer and scheduler.

---

## 📁 Project Architecture

```
TaskPilot-AI/
├── app/
│   ├── core/
│   │   ├── config.py         # Centralized configuration & environment loader
│   │   ├── database.py       # SQLAlchemy engine & session management
│   │   └── security.py       # Bcrypt password hashing & JWT tokens
│   ├── models/               # SQLAlchemy ORM models (User, Conversation, ChatMessage, Task)
│   ├── schemas/              # Pydantic request & response validation schemas
│   ├── api/                  # Modular REST routers (auth, tasks, chat, calendar, gmail)
│   ├── services/             # Core business logic & Groq agent orchestration
│   └── tools/                # Agent tools (calculator, datetime, tavily, tasks, google)
├── alembic/                  # Database migration scripts
├── frontend/                 # Vite + React + Tailwind CSS dashboard
├── tests/                    # Automated pytest test suite
├── api.py                    # Root FastAPI application entrypoint
├── main.py                   # Standalone CLI agent entrypoint
├── gmail_tool.py             # Gmail OAuth integration
├── calendar_tool.py          # Google Calendar OAuth integration
└── requirements.txt          # Python dependencies
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* **Python**: 3.10+ (tested on Python 3.14)
* **Node.js**: v18+ (tested on Node v23)
* **npm**: v9+

### 2. Backend Setup
1. Clone the repository and enter the directory:
   ```bash
   cd TaskPilot-AI
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your environment variables in `.env` (refer to `.env.example`):
   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   DATABASE_URL=postgresql://postgres:password@db.your-supabase-ref.supabase.co:5432/postgres
   SECRET_KEY=your_jwt_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ALGORITHM=HS256
   ```
5. Apply database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the FastAPI backend server:
   ```bash
   uvicorn api:app --reload --port 8000
   ```
   * Interactive Swagger Documentation: `http://localhost:8000/docs`
   * Health Check: `http://localhost:8000/health`

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   * Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

Run the full backend test suite covering authentication, tasks CRUD, AI agent tools, chat history, and Google mocks:

```bash
cd TaskPilot-AI
PYTHONPATH=. venv/bin/pytest -v
```

---

## 🔒 Security & OAuth Configuration

* **Protected Files**: `.env`, `credentials.json`, `token.json`, and `calendar_token.json` are excluded from version control via `.gitignore`.
* **Google Integrations**:
  * Place your Google Cloud OAuth client credentials in `credentials.json`.
  * The first time you authenticate Gmail or Calendar, follow the OAuth prompt to generate `token.json` and `calendar_token.json`.
* **Action Confirmations**: Email sending and calendar event creation will never execute silently; the AI assistant generates an action preview and requires user confirmation.
