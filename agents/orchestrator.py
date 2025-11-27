from agents.base_agent import BaseAgent
from memory.session_manager import SessionManager
from infrastructure.a2a_registry import registry
import json
import asyncio
import importlib
from infrastructure.mcp_server import list_files

class Orchestrator(BaseAgent):
    def __init__(self, session_manager: SessionManager):
        super().__init__(name="Orchestrator")
        self.session_manager = session_manager
        self.agents = {}
        for agent_name in registry.list_agents():
            card = registry.get_agent(agent_name)
            try:
                module = importlib.import_module(card.module_path)
                agent_class = getattr(module, card.class_name)
                self.agents[agent_name] = agent_class()
                self.logger.info(f"Dynamically loaded agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to load agent {agent_name}: {e}")
        
        self.current_file = None
        self.cleaning_result = None
        self.insights = None
        self.hydrate_state()

    def hydrate_state(self):
        if self.session_manager.context:
            self.current_file = self.session_manager.context.get("current_file")
            self.cleaning_result = self.session_manager.context.get("cleaning_result")
            self.insights = self.session_manager.context.get("insights")
            self.logger.info(f"State hydrated: File={self.current_file}")

    async def _handle_qa_fallback(self, user_input: str, default_msg: str):
        if not self.current_file: return default_msg
        import os
        file_path = self.current_file
        if self.cleaning_result and os.path.exists(self.cleaning_result):
            file_path = self.cleaning_result
        elif not os.path.exists(file_path):
            file_path = f"data_storage/{self.current_file}"
        
        if os.path.exists(file_path):
            qa_agent = self.agents.get("QAAgent")
            if qa_agent:
                self.log_step("Routing", "Delegating to QAAgent")
                answer = await qa_agent.answer_question(user_input, file_path)
                return f"💡 **Q&A Insight:**\n{answer}\n\n{default_msg}"
        return default_msg

    async def route_request(self, user_input: str):
        current_state = self.session_manager.state
        self.log_step("Routing", f"Current State: {current_state}, Input: {user_input}")

        if current_state == "IDLE":
            if user_input.lower() == "start":
                files = list_files()
                if not files: return "No files found. Please add a CSV."
                file_list = "\n".join([f"- {f}" for f in files])
                return f"Available files:\n{file_list}\n\nPlease type filename."
            elif user_input.endswith(".csv"):
                self.session_manager.set_state("INGESTING")
                return await self.delegate_to_steward(user_input)
            return "Type 'start' to begin."
            
        elif current_state == "INGESTING":
            if "clean" in user_input.lower() or "yes" in user_input.lower():
                self.session_manager.set_state("CLEANING")
                return await self.run_cleaning_loop()
            return await self._handle_qa_fallback(user_input, "Data ingested. Ready to clean?")

        elif current_state == "CLEANING":
            if "analyze" in user_input.lower() or "yes" in user_input.lower():
                self.session_manager.set_state("ANALYZING")
                return await self.transition_to_analysis()
            return await self._handle_qa_fallback(user_input, "Data cleaned. Ready to analyze?")
            
        elif current_state == "ANALYZING":
            if "report" in user_input.lower() or "yes" in user_input.lower():
                 self.session_manager.set_state("REPORTING")
                 return await self.generate_final_report()
            return await self._handle_qa_fallback(user_input, "Analysis done. Ready for report?")

        elif current_state == "REPORTING":
            if "reset" in user_input.lower():
                self.session_manager.set_state("IDLE")
                self.current_file = None
                self.cleaning_result = None
                self.insights = None
                self.session_manager.context = {} 
                return "System reset."
            return await self._handle_qa_fallback(user_input, "Ask questions or type 'reset'.")
        return "Processing..."

    async def delegate_to_steward(self, filename: str):
        self.log_step("Delegating", f"Steward -> {filename}")
        self.current_file = filename
        self.session_manager.context["current_file"] = filename 
        self.session_manager.session_name = f"Analysis of {filename}"
        
        steward = self.agents.get("Steward")
        if not steward: return "Error: Steward agent missing."
        
        profile = await steward.ingest(filename)
        self.session_manager.add_message("system", f"Data Profile: {profile}")
        
        # CORRECTED: Removed [:200] slice to show full report
        return f"✅ **Steward Analysis Complete**\n\n{profile}\n\n---\n**System:** Ready to clean? (Type 'clean')"

    async def run_cleaning_loop(self):
        self.log_step("Delegating", "Refinery")
        import os
        if not self.current_file: return "Error: No file."
        file_path = self.current_file
        if not os.path.exists(file_path): file_path = f"data_storage/{self.current_file}"

        refinery = self.agents.get("Refinery")
        if not refinery: return "Error: Refinery agent missing."

        self.cleaning_result = await refinery.clean_data(file_path)
        self.session_manager.context["cleaning_result"] = self.cleaning_result
        
        if "Error" in self.cleaning_result: return f"Refinery failed: {self.cleaning_result}"

        self.session_manager.add_message("system", f"Cleaned File: {self.cleaning_result}")
        return f"Refinery finished. Saved to: {self.cleaning_result}\n\nProceed to analysis?"

    async def transition_to_analysis(self):
        self.log_step("Context Compaction", "Preparing analysis...")
        if not self.cleaning_result: return "Error: No cleaned data."

        from infrastructure.mcp_server import get_file_metadata
        import os
        cleaned_filename = os.path.basename(self.cleaning_result)
        schema = get_file_metadata(cleaned_filename)
        
        self.log_step("Delegating", "Analyst Squad")
        analyst_squad = self.agents.get("AnalystSquad")
        if not analyst_squad: return "Error: AnalystSquad missing."

        self.insights = await analyst_squad.run_parallel_analysis(self.cleaning_result, schema)
        self.session_manager.context["insights"] = self.insights
        
        return f"Analyst Squad finished.\n\nProceed to report?"

    async def generate_final_report(self):
        self.log_step("Delegating", "Critic")
        critic = self.agents.get("Critic")
        if not critic: return "Error: Critic missing."
        if not self.insights: return "Error: No insights."

        report = await critic.evaluate_and_report(self.insights)
        return f"FINAL REPORT:\n\n{report}\n\n(Ask questions or type 'reset')"