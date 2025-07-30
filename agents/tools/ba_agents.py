"""
BA Agents - Specialized agents for BA Assistant operations
Handles user chat interactions using the knowledge graph.
"""

from typing import Dict, Any, List, Optional, Annotated
import os
import logging
from datetime import datetime, timezone
from agents.builder.agent_workflow_builder import BAKnowledgeState, BAKnowledgeWorkflowBuilder
from knowledge_graph.business.ba_knowledge_service import BAKnowledgeService
from utils.prompt_loading import prompt_loader
from operator import itemgetter
from langchain.chat_models import ChatOpenAI

class BAKnowledgeAgent:
    """Agent for handling knowledge-based interactions using LLM and knowledge graph."""
    
    # Model to environment variable mapping
    MODEL_API_KEYS = {
        "gpt-4": "OPENAI_API_KEY",
        "gpt-4.1-mini": "OPENAI_API_KEY",
        "gpt-3.5-turbo": "OPENAI_API_KEY",
        "gemini-2.0-flash": "GOOGLE_API_KEY",
    }
    
    def __init__(self, model_name: str = None):
        self.knowledge_service = BAKnowledgeService()
        
        # Load system prompt with better error handling
        self.system_prompt = prompt_loader.load_prompt("ba_assistant_prompt")
        if not self.system_prompt:
            msg = "System prompt could not be loaded. Using fallback prompt."
            logging.error(msg)
            self.system_prompt = """You are a helpful BA assistant. Answer questions {question} using the provided context {context}."""
        
        # Use environment variable with fallback for model name
        self.model_name = model_name or os.getenv("BA_MODEL_NAME", "gpt-4.1-mini")
        
        # Get corresponding API key for the model
        api_key_env = self.MODEL_API_KEYS.get(self.model_name)
        if not api_key_env:
            raise ValueError(f"Unsupported model: {self.model_name}")
            
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API key not found: {api_key_env} environment variable is not set")
            
        logging.info(f"Initializing LLM with model: {self.model_name}")
        
        try:
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.3,
                api_key=api_key
            )
        except Exception as e:
            logging.error(f"Failed to initialize ChatOpenAI with model {self.model_name}: {e}")
            raise

        # Initialize builder and build workflow
        try:
            builder = BAKnowledgeWorkflowBuilder(
                kg_service=self.knowledge_service,
                system_prompt=self.system_prompt,
                llm=self.llm
            )
            self.workflow = builder.build()
        except Exception as e:
            logging.error(f"Failed to build workflow: {e}")
            raise

    async def process_user_query(
        self,
        query: str,
        context_window: int = 5
    ) -> Dict[str, Any]:
        initial_state: BAKnowledgeState = {
            "query": query,
            "context_window": context_window,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = await self.workflow.ainvoke(initial_state)
            return result
        except ValueError as e:
            logging.error(f"Value error in query processing: {e}")
            return self._create_error_response("Invalid input format", query)
        except Exception as e:
            logging.exception("Unexpected error processing user query")
            return self._create_error_response(f"Internal error: {str(e)}", query)

    def _create_error_response(self, message: str, query: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": message,
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }