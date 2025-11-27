# DataGuild: Codebase & Architecture Guide

This document provides a comprehensive deep-dive into the DataGuild codebase. It explains the purpose of every file, the system architecture, and the detailed workflow of how data and control flow through the system.

---

## 1. System Architecture Overview

DataGuild is an **Autonomous Multi-Agent System** built on the **Google Agent Development Kit (ADK)**. It mimics a real-world data science team where specialized agents collaborate to solve complex data problems.

### Core Concepts
*   **Orchestrator Pattern**: A central "manager" agent (`Orchestrator`) controls the workflow, delegating tasks to specialized "worker" agents.
*   **Google ADK**: The underlying framework. Every agent is a `google.adk.Agent` executed by a `google.adk.Runner` within a `google.adk.Session`.
*   **Asynchronous Execution**: The system uses Python's `asyncio` to handle long-running tasks (like data cleaning or parallel analysis) without blocking.
*   **Context Compaction**: To manage LLM context windows, the system periodically summarizes conversation history and flushes the raw logs, keeping only the essential insights.

---

## 2. Workflow & Data Flow

The system operates as a **State Machine** managed by the `SessionManager`.

### The Pipeline
1.  **Initialization**: `main.py` initializes the system. The state is `IDLE`.
2.  **Ingestion (Steward)**:
    *   User provides a CSV file.
    *   **Orchestrator** delegates to **Steward**.
    *   **Steward** reads the file metadata (columns, types) using `mcp_server.py`.
    *   **Steward** generates a "Data Profile" (description, quality issues).
    *   *State Transition*: `IDLE` -> `INGESTING` -> `CLEANING`.
3.  **Cleaning (Refinery)**:
    *   **Orchestrator** delegates to **Refinery**.
    *   **Refinery** enters a loop: Audit -> Plan Fix -> Execute Fix -> Verify.
    *   It uses `pandas` (simulated or real execution) to fix missing values or types.
    *   *State Transition*: `CLEANING` -> `ANALYZING`.
4.  **Context Compaction**:
    *   Before analysis, the **Orchestrator** triggers a summary of the cleaning phase.
    *   Old chat history is cleared; only the summary is retained in memory.
5.  **Analysis (Analyst Squad)**:
    *   **Orchestrator** delegates to **AnalystSquad**.
    *   **AnalystSquad** spawns 3 sub-agents in parallel:
        *   **UniAgent**: Univariate analysis (distributions).
        *   **BiAgent**: Bivariate analysis (correlations).
        *   **TrendAgent**: Time-series analysis.
    *   Results are aggregated into a single "Insights" object.
    *   *State Transition*: `ANALYZING` -> `REPORTING`.
6.  **Reporting (Critic)**:
    *   **Orchestrator** delegates to **Critic**.
    *   **Critic** reviews the insights.
    *   **Critic** uses **Google Search** (`tools/search_tool.py`) to find real-world context (e.g., "Why did sales drop in Jan 2024?").
    *   **Critic** generates the Final Report.
    *   *State Transition*: `REPORTING` -> `IDLE`.

---

## 3. File-by-File Breakdown

### Root Directory
*   **`main.py`**: The entry point. It sets up the `SessionManager` and `Orchestrator`, and runs the main input loop (`asyncio.run(main_loop())`). It handles user input and prints agent responses.
*   **`config.py`**: Configuration hub. Manages API keys (with rotation logic), model names (`gemini-2.5-flash`), and file paths. It automatically sets the `GOOGLE_API_KEY` environment variable for ADK.
*   **`requirements.txt`**: List of Python dependencies (`google-adk`, `google-genai`, `pandas`, `plotly`, `python-dotenv`, `opentelemetry-api`, etc.).
*   **`verify_system.py`**: An automated test script. It runs the entire pipeline using dummy data to verify that all agents and tools are working correctly.

### `agents/` (The Workforce)
*   **`base_agent.py`**: **CRITICAL FILE**. The base class for all agents.
    *   **ADK Integration**: Wraps `google.adk.Agent` and `google.adk.Runner`.
    *   **`generate()`**: The core method. It creates a `Session`, initializes a `Runner`, sends the prompt, and extracts the response from the `session.events` stream.
    *   **Logging**: Handles "Thinking" logs and step tracking.
*   **`orchestrator.py`**: The manager. Inherits from `BaseAgent`.
    *   **`route_request()`**: Determines the next step based on `SessionManager.state`.
    *   **Delegation**: Methods like `delegate_to_steward()` call other agents.
*   **`steward.py`**: Data Ingestion Agent.
    *   **`ingest()`**: Uses `get_file_metadata` to understand the dataset structure and prompts the LLM to create a profile.
*   **`refinery.py`**: Data Cleaning Agent.
    *   **`clean_data()`**: Implements the Audit-Fix-Verify loop.
    *   **`plan_fix()`**: Asks LLM for pandas code to fix data issues.
*   **`analyst_squad.py`**: Parallel Analysis Team.
    *   **`Analyst`**: A generic analysis agent.
    *   **`AnalystSquad`**: Manages 3 `Analyst` instances. Uses `asyncio.gather()` to run them simultaneously.
*   **`critic.py`**: Reporting Agent.
    *   **`evaluate_and_report()`**: Performs a Google Search to ground insights and generates the final narrative.

### `memory/` (The Brain)
*   **`session_manager.py`**: Manages the conversation state (`IDLE`, `CLEANING`, etc.) and history.
    *   **`summarize_and_flush()`**: Implements the context compaction logic.
*   **`memory_bank.py`**: Persistent storage.
    *   Uses `chromadb` to store embeddings of summaries and past interactions (Long-term memory).

### `infrastructure/` (The Backbone)
*   **`mcp_server.py`**: Model Context Protocol server. Provides safe functions for agents to read local files (`get_file_metadata`, `read_dataset`).
*   **`observability.py`**: Sets up OpenTelemetry tracing to visualize agent workflows and performance.
*   **`a2a_registry.py`**: Agent-to-Agent Registry. Defines "Agent Cards" that describe capabilities, inputs, and outputs (useful for dynamic discovery).

### `tools/` (The Toolkit)
*   **`search_tool.py`**: Wrapper for the Serper API (Google Search). Used by the **Critic** agent.
*   **`data_ops.py`**: Helper functions for pandas operations (loading data, summary stats).
*   **`visualizer.py`**: Helper functions for generating Plotly charts.

---

## 4. How Things Are Handled

### Google ADK Integration
Instead of raw API calls, we use the ADK's abstractions:
```python
# From agents/base_agent.py
self.agent = Agent(model=self.model, name=name)
runner = Runner(agent=self.agent, session_service=session_service, app_name="DataGuild")
for event in runner.run(...):
    # Process events
```
This ensures we follow best practices for session management and agent execution.

### Error Handling
*   **`BaseAgent`**: Catches execution errors and logs them.
*   **`Refinery`**: Has a retry loop. If a cleaning step fails, it can retry (up to `max_loops`).
*   **`verify_system.py`**: Catches exceptions at each stage (Ingestion, Cleaning, etc.) to report PASS/FAIL status.

### Parallelism
We use Python's `asyncio` library. The `Orchestrator` and `BaseAgent` methods are `async`. The `AnalystSquad` specifically leverages this to run three LLM calls at once, significantly reducing the total time for analysis.
