# DataGuild: An Autonomous Data Intelligence System

**DataGuild** is a sophisticated multi-agent system designed to autonomously ingest, clean, analyze, and report on complex datasets. Built on the **Google Agent Development Kit (ADK)**, it leverages a guild of specialized AI agents to perform end-to-end data science workflows.

## 🚀 Key Features

*   **Google ADK Powered**: Utilizes `google.adk` for robust agent orchestration, session management, and runner execution.
*   **Multi-Agent Architecture**:
    *   **Orchestrator**: The central state machine that manages workflow transitions and delegates tasks.
    *   **Steward**: Handles data ingestion, metadata extraction, and privacy checks.
    *   **Refinery**: Autonomously audits and cleans data (e.g., imputing missing values).
    *   **Analyst Squad**: A parallelized team of agents performing Univariate, Bivariate, and Trend analysis simultaneously.
    *   **Critic**: Evaluates insights and grounds them with real-world context using **Google Search**.
*   **Context Compaction**: Intelligent memory management to summarize long sessions and maintain context window efficiency.
*   **Observability**: Integrated OpenTelemetry tracing for monitoring agent steps and "thinking" processes.
*   **Local Data Access**: Secure local file interaction via a custom MCP (Model Context Protocol) server.

## 🛠️ Architecture

The system follows a state-driven workflow:
`IDLE` -> `INGESTING` -> `CLEANING` -> `ANALYZING` -> `REPORTING`

1.  **User Input**: Initiates the process via CLI.
2.  **Orchestrator**: Routes the request to the appropriate specialized agent.
3.  **Agents**: Execute tasks using Google's Gemini models (via ADK Runner).
4.  **Memory Bank**: Stores session history and summaries (ChromaDB).
5.  **Tools**: Agents utilize tools like Pandas, Plotly, and Google Search.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Data_agent
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    *   Create a `.env` file in the root directory.
    *   Add your API keys (Google Gemini and Serper/Google Search):
        ```env
        GEMINI_API_KEYS=your_gemini_key_1,your_gemini_key_2,...
        SERPER_API_KEY=your_serper_key
        ```
    *   *Note: The system supports API key rotation automatically.*

## ▶️ Usage

1.  **Start the Application**:
    ```bash
    python main.py
    ```

2.  **Interact**:
    *   **Start**: Type `start` or provide a CSV filename (e.g., `complex_data.csv`).
    *   **Ingest**: The Steward will profile the data.
    *   **Clean**: Type `clean` or `yes` to authorize data cleaning.
    *   **Analyze**: Type `analyze` or `yes` to dispatch the Analyst Squad.
    *   **Report**: Type `report` or `yes` to generate the final critical report.
    *   **Reset**: Type `reset` to clear the session and start over.
    *   **Exit**: Type `exit` to quit.

## 🧪 Verification

To run the automated end-to-end verification suite:
```bash
python verify_system.py
```
This script simulates a full user interaction flow using dummy data to ensure all agents are functioning correctly.

## Project Structure

*   `agents/`: Source code for all agents (`base_agent.py`, `orchestrator.py`, etc.).
*   `infrastructure/`: Observability, MCP server, and Agent Registry.
*   `memory/`: Session management and Vector DB logic.
*   `tools/`: Utility scripts for data operations and search.
*   `config.py`: Central configuration and Auth setup.
*   `main.py`: Application entry point.

---
*Powered by Google Gemini & Google ADK*
