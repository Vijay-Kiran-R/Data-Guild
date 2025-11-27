# 📘 DataGuild: Technical Architecture & Codebase Guide

This document serves as the comprehensive technical manual for **DataGuild**. It details the architectural decisions, the Google ADK implementation, and the internal mechanics of the "Autonomous Guild" workflow.

---

## 1. System Architecture: The Guild Flow

DataGuild operates as a **Finite State Machine (FSM)** where a central Orchestrator manages a pipeline of specialized agents.

### 🏛️ Core Components
* **Orchestrator** (`agents/orchestrator.py`): The state machine manager. It routes user input to the correct agent based on the current state (`INGESTING`, `CLEANING`, `ANALYZING`, etc.).
* **Persistent Storage**:
    * **ChromaDB** (`memory/memory_bank.py`): Stores long-term vector embeddings of insights and schema definitions.
    * **MCP Server** (`infrastructure/mcp_server.py`): A secure file server that agents use to read/write CSVs, enforcing a strict sandbox around `data_storage/`.

---

## 2. Google ADK Implementation

The system is built entirely on the **Google Agent Development Kit (ADK)**. Here is how we utilize its core primitives:

### 2.1 Agent & Runner (`agents/base_agent.py`)
* **`google.adk.Agent`**: Defines the "persona". We inject the specific system instructions (e.g., "You are a Critic...") and tools into this class.
* **`google.adk.Runner`**: The execution engine. Instead of raw API calls, we pass the `Agent` and a `Session` to the `Runner`. It handles the ReAct (Reason-Act-Observe) loop automatically.

### 2.2 Ephemeral Sessions (`agents/base_agent.py`)
* **`InMemorySessionService`**: We create lightweight, ephemeral sessions for specific tasks.
    * *Design Choice*: When the `UniAgent` calculates skewness, it spins up a fresh session, performs the math, and destroys the session. This keeps the global context window clean and focused.

### 2.3 Native Tools (`tools/search_tool.py`)
* **`google.adk.tools.google_search`**: We use the native ADK search tool for the **Critic Agent**. This provides grounded, citation-backed search results directly from Google.

---

## 3. File-by-File Breakdown

### 📂 Root Directory (Entry & Config)

#### `main.py`
* **What it Does**: The CLI entry point.
* **Functionality**: Initializes `SessionManager` and `Orchestrator`. It manages the user loop and intercepts system commands like `start` (which triggers the Native File Browser).
* **Role**: Acts as the interface layer, ensuring user inputs are correctly routed to the AI core.

#### `config.py`
* **What it Does**: Central configuration hub.
* **Functionality**: Loads `.env` and implements an **API Key Rotation** cycle (`itertools.cycle`). It automatically switches between multiple Gemini API keys to ensure high availability during heavy parallel testing.

---

### 🧠 `agents/` (The Intelligence Core)

#### `base_agent.py`
* **What it Does**: Parent class for all agents.
* **Functionality**: Wraps Google ADK primitives. It creates a fresh `InMemorySession` for every `generate()` call, ensuring that agent "thoughts" are execution-isolated from the main conversation history.

#### `orchestrator.py`
* **What it Does**: The "Manager" and State Machine.
* **Functionality**: Monitors `session_manager.state`. Delegates tasks to `Steward` (Ingest), `Refinery` (Clean), or `AnalystSquad` (Analyze). It proactively detects non-command inputs and routes them to the `QAAgent`.

#### `analyst_squad.py`
* **What it Does**: The "Deep Analysis Engine" (Hybrid Parallel Architecture).
* **Functionality**:
    * **`AnalystSquad`**: Leverages `asyncio.gather` to execute 3 agents (`Uni`, `Bi`, `Trend`) in parallel.
    * **`LeadAnalyst`**: A meta-agent that reviews aggregated findings and generates a `DeepDivePlan` (JSON) to spawn specific follow-up tasks.
    * **`Analyst`**: The worker that generates Python code, executes it in a sandbox, and auto-retries on error.

#### `refinery.py`
* **What it Does**: The "Data Engineer".
* **Functionality**: Implements a **Self-Healing Loop**: Audit -> Plan -> Code -> Execute -> Catch Error -> Retry. It produces clean data artifacts (CSVs) for downstream analysis.

#### `steward.py`
* **What it Does**: The "Gatekeeper".
* **Functionality**: Calls `mcp_server` to profile file headers and uses `search_tool` to research domain context (e.g., "What does ICD-10 mean?") before analysis begins.

#### `critic.py`
* **What it Does**: The "Director".
* **Functionality**: Fetches insights from memory, verifies them with **Google Search**, and synthesizes the final Markdown report for the user.

#### `qa_agent.py`
* **What it Does**: Stateless Ad-Hoc Q&A.
* **Functionality**: Called when user input is a question ("How many rows?"). It loads data, answers the specific query, and exits without altering the global workflow state.

---

### 🔌 `infrastructure/` (The Backbone)

#### `mcp_server.py`
* **What it Does**: Custom **Model Context Protocol (MCP)** server.
* **Functionality**: Provides safe file tools (`read_dataset`, `list_files`). It enforces a strict **Sandbox** around `data_storage/`, ensuring agents only modify approved datasets.

#### `observability.py`
* **What it Does**: OpenTelemetry Tracing.
* **Functionality**: Wraps agent execution to capture spans (steps) and attributes. It saves traces to `logs/telemetry_logs/` for visualizing the "Chain of Thought" waterfall.

#### `file_browser.py`
* **What it Does**: Native OS File Dialog.
* **Functionality**: Uses `tkinter` to open a system window, allowing users to select files graphically even while running in a CLI environment.

#### `a2a_registry.py`
* **What it Does**: Service Discovery.
* **Functionality**: A registry of "Agent Cards" allowing the Orchestrator to dynamically load agents based on capabilities.

---

### 💾 `memory/` (The Brain)

#### `memory_bank.py`
* **What it Does**: **ChromaDB** Interface.
* **Functionality**: Stores embeddings for Insights and Schemas, enabling the system to recall past findings or user preferences across sessions.

#### `session_manager.py`
* **What it Does**: Context Compaction & State Management.
* **Functionality**: Tracks state (`CLEANING`, etc.). When a phase ends, it calls `summarize_and_flush()` to compress 50+ turns of "thinking" logs into a concise summary, freeing up token space.

#### `file_session_service.py`
* **What it Does**: Session Persistence.
* **Functionality**: Serializes session state to JSON in `session_storage/`, allowing users to pause and resume workflows seamlessly.

---

### 🛠️ `tools/` (The Toolkit)

#### `search_tool.py`
* **What it Does**: Exposes `google.adk.tools.google_search`.
* **Functionality**: Provides direct access to Google's index for grounded verification.

#### `knowledge_client.py`
* **What it Does**: Knowledge Base Interface.
* **Functionality**: Simulates fetching corporate validation rules. Designed as an interface pattern to be easily swapped with a real enterprise API.

#### `visualizer.py` & `data_ops.py`
* **What it Does**: Pandas/Plotly Wrappers.
* **Functionality**: Modular functions that agents call to generate plots and statistics reliably.

---

## 4. Data Lifecycle

1.  **Ingestion**: User picks `raw.csv`. **Steward** creates a profile.
2.  **Cleaning**: **Refinery** creates `cleaned_raw.csv`.
3.  **Analysis**: **Analyst Squad** generates plots.
    * *Artifacts*: PNG charts are saved to `static/plots/`.
4.  **Reporting**: **Critic** generates a Report.
    * *Artifacts*: Final report text is displayed and saved to session history.

---

## 5. Extending DataGuild

To add a new capability (e.g., Machine Learning):

1.  **Create Agent**: `agents/ml_engineer.py` (Inherit from `BaseAgent`).
2.  **Register**: Add to `infrastructure/a2a_registry.py`.
3.  **Update Orchestrator**: Add a `TRAINING` state in `orchestrator.py` and route `train` commands to your new agent.