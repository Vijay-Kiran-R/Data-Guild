# 🤖 DataGuild: The Autonomous Data Intelligence System

![Google GenAI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Framework](https://img.shields.io/badge/Powered%20by-Google%20ADK-34A853?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20Guild-orange?style=for-the-badge)

> **"The 24/7 Surgical Team for Your Data."**

**DataGuild** is an fully automated self sustaining Multi-Agent System (MAS) designed to autonomously ingest, clean, analyze, and report on datasets. Unlike standard chatbots, DataGuild acts as a **collaborative agency** of specialized AI workers that perform end-to-end data science workflows from fixing dirty data to generating strategic C-suite reports without human intervention.

Built on the **Google Agent Development Kit (ADK)**, it features a unique **Iterative Deep Analysis Engine** that mimics a real-world data team: iterating, verifying, and digging deeper until the full story is revealed.

---

## 🔄 Autonomous Agent Guild Flow

The system operates as a strict pipeline of specialized stages, orchestrated by a central state machine.

![Autonomous Agent Guild Flow](Data_agent/Data_Guild_WorkFlow.png)

---

## 🔧 Google ADK Implementation

This project heavily leverages the **Google Agent Development Kit (ADK)** to manage agent lifecycle, state, and tool execution. Here is the technical breakdown of how ADK is utilized in the codebase:

### 1. Agent & Runner Architecture
* **File**: `agents/base_agent.py`
* **Usage**:
    * **`google.adk.Agent`**: We use this core class to define the persona, model, and system instructions for every agent (e.g., Critic, Refinery). It serves as the container for the agent's configuration.
    * **`google.adk.Runner`**: This is the execution engine. Instead of manually calling the model API, we pass our `Agent` and `Session` to the `Runner`. The Runner handles the event loop, processes tool calls automatically, and manages the "think-act-observe" cycle.

### 2. Session Management
* **File**: `agents/base_agent.py`
* **Usage**:
    * **`google.adk.sessions.InMemorySessionService`**: We utilize this service to create ephemeral sessions for specific tasks. This ensures that when an agent (like the `UniAgent`) performs a specific calculation, it does so in a clean, isolated context that doesn't pollute the global history.

### 3. Native Tool Integration
* **File**: `tools/search_tool.py`
* **Usage**:
    * **`google.adk.tools.google_search`**: We import the pre-built Google Search tool directly from the ADK. This provides the **Critic Agent** with grounded, real-time access to the web without needing third-party wrappers like Serper or Bing.

### 4. Model Wrapper
* **File**: `agents/base_agent.py` & `config.py`
* **Usage**:
    * **`google.adk.models.Gemini`**: The ADK provides a standardized interface for Gemini models. We use this wrapper to inject `gemini-2.5-flash` into our agents, ensuring compatibility with the Runner's event stream.

---

## 🚀 Key Innovations & Features

### 1. ⚡ Deep Analysis Engine (Analyst Squad)
DataGuild leverages `asyncio` to spawn a **Parallel Analyst Squad**:
* **Wide Scan**: `UniAgent`, `BiAgent`, and `TrendAgent` execute simultaneously, cutting analysis time by **60%**.
* **Iterative Deep Dives**: A **Lead Analyst** reviews findings and dynamically spawns new tasks to investigate anomalies.

### 2. 🛡️ Self-Healing Data Refinery
The **Refinery Agent** possesses a **Code-Correction Loop**:
* **Audit & Fix**: Writes Pandas code to fix nulls and types.
* **Auto-Heal**: If the code fails (e.g., `KeyError`), it catches the traceback, rewrites its own code, and retries automatically.

### 3. 🧠 Context Compaction (Memory Efficiency)
To maintain efficiency within LLM token limits:
* **Summarization**: Verbose logs are compressed into concise summaries after each phase.
* **Flush & Store**: Raw logs are cleared, and key insights are embedded into **ChromaDB** for long-term retrieval.

### 4. 📂 Native File Browsing & Persistence
* **Browse System**: Includes a **"Browse System"** feature to select datasets using your OS's native file dialog.
* **Session Persistence**: Workflows are saved as JSON. You can `exit` and resume analysis later exactly where you left off.

### 5. 🌐 Grounded Verification (Critic)
The **Critic Agent** prevents hallucinations by verifying insights against the real world using **Google Search**.
* *Check*: "Sales dropped in March 2020." -> *Search*: "Covid lockdowns." -> *Result*: Verified correlation.

### 6. 📡 Enterprise Observability
* **OpenTelemetry Tracing**: The system features integrated tracing to monitor every agent step, tool call, and "thought process" for debugging and performance tuning.

### 7. 🔒 Secure Data Architecture
* **Local Data Access (MCP)**: Files are accessed via a custom **Model Context Protocol (MCP)** server, ensuring agents only touch whitelisted data.
* **Knowledge Base Integration**: Includes a mock client to fetch domain-specific validation schemas, ensuring data adheres to business rules.
---

## 🛠️ Architecture

The system follows a state-driven workflow:
`IDLE` -> `INGESTING` -> `CLEANING` -> `ANALYZING` -> `REPORTING`

1.  **User Input**: Initiates the process via CLI.
2.  **Orchestrator**: Routes the request to the appropriate specialized agent.
3.  **Agents**: Execute tasks using Google's Gemini models (via ADK Runner).
4.  **Memory Bank**: Stores session history and summaries (ChromaDB).
5.  **Tools**: Agents utilize tools like Pandas, Plotly, Google Search, and a Mock Knowledge Client.

---

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Vijay-Kiran-R/Data-Guild.git 
    cd Data-Guild
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    * Create a `.env` file in the root directory.
    * Add your API keys (supports rotation):
        ```env
        GEMINI_API_KEYS=your_key_1,your_key_2,...
        ```

---

## ▶️ Usage

1.  **Start the Application**:
    ```bash
    python main.py
    ```

2.  **Interact**:
    * **Start**: Type `start`. You can enter a filename or select **[B] Browse System** to pick a file graphically.
    * **Ingest**: The Steward will profile the data and check against domain schemas.
    * **Clean**: Type `clean` or `yes` to authorize the Refinery's self-healing loop.
    * **Analyze**: Type `analyze` or `yes` to dispatch the Analyst Squad.
    * **Report**: Type `report` or `yes` to generate the final critical report.
    * **Q&A**: Ask any question about your data (e.g., "What is the average sales?"). The system detects it's not a command and routes it to the **QA Agent** for a direct answer.
    * **Visuals**: All generated charts (PNG) are automatically saved to `static/plots/`. You can view them there to verify the Analyst Squad's findings.
    * **Reset**: Type `reset` to clear the session and start over.
    * **Exit**: Type `exit` to quit (prompts to save session).

---

## 📂 Project Structure

```text
DataGuild/
├── agents/                     # 🧠 The Intelligence Core
│   ├── orchestrator.py         # State Machine & Delegation Logic
│   ├── analyst_squad.py        # Parallel & Iterative Analysis Engine (The "Hive Mind")
│   ├── refinery.py             # Self-Healing Data Cleaning Agent
│   ├── steward.py              # Data Ingestion & Profiling Agent
│   ├── critic.py               # Verification & Reporting Agent
│   ├── qa_agent.py             # Ad-hoc Question Answering Agent
│   └── base_agent.py           # ADK Wrapper & Runner Configuration
│
├── infrastructure/             # 🔌 The Backbone
│   ├── mcp_server.py           # Secure File System Access (Model Context Protocol)
│   ├── observability.py        # OpenTelemetry Tracing & Metrics
│   ├── file_browser.py         # Native OS File Dialog Integration
│   ├── stream_handler.py       # Real-time Console Logging
│   └── a2a_registry.py         # Agent Service Discovery Registry
│
├── memory/                     # 💾 The Brain
│   ├── memory_bank.py          # ChromaDB Vector Store Interface
│   ├── session_manager.py      # Context Compaction & State Management
│   └── file_session_service.py # JSON-based Session Persistence
│
├── tools/                      # 🛠️ The Toolkit
│   ├── data_ops.py             # Pandas Data Manipulation Scripts
│   ├── visualizer.py           # Plotly/Matplotlib Chart Generators
│   ├── search_tool.py          # Google Search Integration
│   └── knowledge_client.py     # Mock Domain Knowledge Base
│
├── data_storage/               # 📂 Input/Output Sandbox
│   └── (Drop your CSV files here for processing)
│
├── static/                     # 📊 Generated Artifacts
│   └── plots/                  # Analysis Charts (PNGs) saved here
│
├── logs/                       # 🔍 Debugging & Auditing
│   ├── agent_logs/             # Readable conversation logs per session
│   └── telemetry_logs/         # OpenTelemetry traces for performance debugging
│
├── session_storage/            # 💾 Persistence
│   └── (Saved session states as .json files)
│
├── chroma_db/                  # 🧠 Long-term Vector Memory (SQLite)
├── main.py                     # 🏁 Application Entry Point
├── config.py                   # ⚙️ Configuration & API Key Rotation
├── requirements.txt            # 📦 Python Dependencies
└── .env                        # 🔑 API Keys (GitIgnored)
---
*Powered by Google Gemini & Google ADK*