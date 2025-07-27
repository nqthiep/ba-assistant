"""
Chat Lifecycle Handler for Chainlit UI
Handles chat initialization, welcome messages, and system setup.
Follows Single Responsibility Principle - only manages chat lifecycle.
"""

import chainlit as cl
from typing import List, Dict, Any
from .base_handler import BaseChainlitHandler
from .response_formatter import ResponseFormatter


class ChatLifecycleHandler(BaseChainlitHandler):
    """
    Handles chat lifecycle events and system initialization.
    
    Responsibilities:
    - Chat start event handling
    - Welcome message display
    - Knowledge system status checking
    - Initial system setup
    
    Follows SOLID principles:
    - Single Responsibility: Only handles chat lifecycle
    - Dependency Inversion: Uses BA Knowledge Service abstraction
    """
    
    def __init__(self, factory):
        """
        Initialize chat lifecycle handler.
        
        Args:
            factory: KnowledgeGraphFactory for dependency injection
        """
        super().__init__(factory)
        self.commands = [
            {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
            {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True},
            {"id": "Clear knowledge graph", "icon": "trash", "description": "Clear knowledge graph", "button": True},
        ]
    
    async def handle(self, *args, **kwargs) -> None:
        """
        Main handler method for chat lifecycle events.
        Currently delegates to on_chat_start.
        """
        await self.on_chat_start()
    
    async def on_chat_start(self) -> None:
        """
        Handle chat start event.
        
        - Sets up commands
        - Displays welcome message
        - Checks knowledge system status
        - Initializes system if needed
        """
        # Set up Chainlit commands
        await cl.context.emitter.set_commands(self.commands)
        
        # Display welcome message
        welcome_content = ResponseFormatter.format_welcome_message()
        await self.send_message(welcome_content)
        
        # Check knowledge system status
        status = await self.ba_knowledge.get_knowledge_status()
        print(f"Status: {status} and has data: {status.get('has_data', False)}")
        
        # Initialize system if no data exists
        if not status.get("has_data", False):
            await self._initialize_knowledge_system()
    
    async def _initialize_knowledge_system(self) -> None:
        """
        Initialize the knowledge system if it's empty.
        
        - Calls BA knowledge service to initialize
        - Handles success/error responses
        - Triggers file upload request on success
        """
        init_result = await self.ba_knowledge.initialize_knowledge_system()
        
        if init_result.get("status") == "success":
            # Import FileHandler here to avoid circular imports
            from .file_handler import FileHandler
            file_handler = FileHandler(self.factory)
            await file_handler.ask_file_source()
            
            success_message = ResponseFormatter.format_initialization_success()
            await self.send_message(success_message)
        else:
            error_message = ResponseFormatter.format_initialization_error(init_result)
            await self.send_message(error_message)
    
    def get_available_commands(self) -> List[Dict[str, Any]]:
        """
        Get list of available commands for the chat interface.
        
        Returns:
            List of command dictionaries with id, icon, description, and button flag
        """
        return self.commands.copy()
    
    async def set_custom_commands(self, commands: List[Dict[str, Any]]) -> None:
        """
        Set custom commands for the chat interface.
        Useful for future extensibility with different command sets.
        
        Args:
            commands: List of command dictionaries to set
        """
        self.commands = commands
        await cl.context.emitter.set_commands(self.commands)
