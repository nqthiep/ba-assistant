"""
Base Handler for Chainlit UI Interactions
Provides common functionality for all specialized handlers.
Follows Single Responsibility Principle and Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
import chainlit as cl
from knowledge_graph import KnowledgeGraphFactory


class BaseChainlitHandler(ABC):
    """
    Abstract base class for all Chainlit handlers.
    Provides common dependencies and enforces handler interface.
    
    Follows SOLID principles:
    - Single Responsibility: Each handler has one specific purpose
    - Dependency Inversion: Depends on abstractions (factory pattern)
    """
    
    def __init__(self, factory: KnowledgeGraphFactory):
        """
        Initialize handler with knowledge graph factory.
        
        Args:
            factory: KnowledgeGraphFactory instance for dependency injection
        """
        self.factory = factory
        self.ba_knowledge = factory.get_ba_knowledge_service()
    
    @abstractmethod
    async def handle(self, *args, **kwargs):
        """
        Abstract method that must be implemented by all handlers.
        Defines the main handling logic for each specialized handler.
        """
        pass
    
    async def send_message(self, content: str) -> None:
        """
        Common utility method to send messages to Chainlit UI.
        
        Args:
            content: Message content to send
        """
        await cl.Message(content=content).send()
    
    async def send_error_message(self, error: str) -> None:
        """
        Common utility method to send error messages to Chainlit UI.
        
        Args:
            error: Error message to send
        """
        await cl.Message(content=f"❌ **Error:** {error}").send()
    
    async def send_success_message(self, message: str) -> None:
        """
        Common utility method to send success messages to Chainlit UI.
        
        Args:
            message: Success message to send
        """
        await cl.Message(content=f"✅ **Success:** {message}").send()
