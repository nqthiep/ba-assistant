"""
Message Handler for Chainlit UI
Handles user message processing and query responses.
Follows Single Responsibility Principle - only manages message processing.
"""

import chainlit as cl
from .base_handler import BaseChainlitHandler
from .response_formatter import ResponseFormatter
from ..constants import UIMessages


class MessageHandler(BaseChainlitHandler):
    """
    Handles user message processing and query responses.
    
    Responsibilities:
    - Processing user text messages
    - Performing knowledge graph searches
    - Formatting and sending search results
    - Future: Integration with LangGraph agents
    
    Follows SOLID principles:
    - Single Responsibility: Only handles message processing
    - Open/Closed: Ready for extension with agent integration
    - Dependency Inversion: Uses BA Knowledge Service abstraction
    """
    
    def __init__(self, factory):
        """
        Initialize message handler.
        
        Args:
            factory: KnowledgeGraphFactory for dependency injection
        """
        super().__init__(factory)
        # Future: Agent integration placeholder
        self.agent = None
        self.use_agent = False
    
    async def handle(self, message_content: str) -> None:
        """
        Main handler method for message processing.
        
        Args:
            message_content: User message content to process
        """
        await self.handle_user_query(message_content)
    
    async def handle_user_query(self, user_input: str) -> None:
        """
        Handle user query messages.
        
        Routes to agent if available, otherwise uses direct knowledge search.
        
        Args:
            user_input: User input string to process
        """
        if self.use_agent and self.agent:
            await self._handle_with_agent(user_input)
        else:
            await self._handle_direct_search(user_input)
    
    async def _handle_direct_search(self, user_input: str) -> None:
        """
        Handle user query with direct knowledge graph search.
        
        Args:
            user_input: User input string to search
        """
        # Use Layer 3 for business knowledge search with formatting
        formatted_result = await self.ba_knowledge.search_business_knowledge(user_input)
        
        # Format and send the search result
        response = ResponseFormatter.format_search_result(formatted_result)
        await self.send_message(response)
    
    async def _handle_with_agent(self, user_input: str) -> None:
        """
        Handle user query with LangGraph agent integration.
        Future implementation for agent-based processing.
        
        Args:
            user_input: User input string to process with agent
        """
        # Future implementation for LangGraph agent integration
        # This method provides the foundation for agent-based message processing
        
        # Placeholder implementation
        await self.send_message(UIMessages.AGENT_NOT_IMPLEMENTED)
        
        # Future implementation would include:
        # 1. Agent initialization and configuration
        # 2. Context preparation for the agent
        # 3. Agent execution with user input
        # 4. Result processing and formatting
        # 5. Response generation and sending
    
    def enable_agent_mode(self, agent) -> None:
        """
        Enable agent-based message processing.
        Future method for LangGraph agent integration.
        
        Args:
            agent: LangGraph agent instance to use
        """
        self.agent = agent
        self.use_agent = True
    
    def disable_agent_mode(self) -> None:
        """
        Disable agent-based message processing.
        Falls back to direct knowledge search.
        """
        self.agent = None
        self.use_agent = False
    
    def is_agent_enabled(self) -> bool:
        """
        Check if agent mode is currently enabled.
        
        Returns:
            True if agent mode is enabled, False otherwise
        """
        return self.use_agent and self.agent is not None
    
    async def process_structured_query(self, query_data: dict) -> None:
        """
        Process structured query data.
        Future method for handling complex query structures from agents.
        
        Args:
            query_data: Structured query data dictionary
        """
        # Future implementation for structured query processing
        # Useful for agent-generated queries with specific parameters
        pass
    
    async def handle_follow_up_question(self, context: str, question: str) -> None:
        """
        Handle follow-up questions with context.
        Future method for contextual conversation handling.
        
        Args:
            context: Previous conversation context
            question: Follow-up question to process
        """
        # Future implementation for contextual question handling
        # Useful for maintaining conversation state and context
        pass
