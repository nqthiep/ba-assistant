"""
BA Agents - Specialized agents for BA Assistant operations
Handles user chat interactions using the knowledge graph.
"""

from typing import Dict, Any, List, Optional, Annotated
import os
from datetime import datetime, timezone
from agents.builder.agent_workflow_builder import BAKnowledgeState, BAKnowledgeWorkflowBuilder
from knowledge_graph.business.ba_knowledge_service import BAKnowledgeService
from utils.prompt_loading import prompt_loader
from operator import itemgetter
from langchain.chat_models import ChatOpenAI

class BAKnowledgeAgent:
    """Agent for handling knowledge-based interactions using LLM and knowledge graph."""
    
    def __init__(self):
        self.knowledge_service = BAKnowledgeService()
        self.system_prompt     = prompt_loader.load_prompt("ba_assistant_prompt")
        self.llm = ChatOpenAI(
            model_name="gpt-4.1-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Khởi tạo builder và build workflow
        builder = BAKnowledgeWorkflowBuilder(
            kg_service=self.knowledge_service,
            system_prompt=self.system_prompt,
            llm=self.llm
        )
        self.workflow = builder.build()

    async def process_user_query(
        self,
        query: str,
        context_window: int = 5
    ) -> Dict[str, Any]:
        initial_state: BAKnowledgeState = {
            "query":          query,
            "context_window": context_window,
            "timestamp":      datetime.now(timezone.utc).isoformat()
        }
        try:
            result = await self.workflow.ainvoke(initial_state)
            return result
        except Exception as e:
            return {
                "status":  "error",
                "message": f"Failed: {str(e)}",
                "query":   query,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }