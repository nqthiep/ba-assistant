"""
Command Handler for Chainlit UI
Handles all command-based interactions and actions.
Follows Single Responsibility Principle - only manages command processing.
"""

import chainlit as cl
from .base_handler import BaseChainlitHandler
from .response_formatter import ResponseFormatter
from ..constants import Commands, UIMessages


class CommandHandler(BaseChainlitHandler):
    """
    Handles command-based user interactions.
    
    Responsibilities:
    - Processing command messages
    - Routing to appropriate command handlers
    - Managing command-specific logic
    
    Follows SOLID principles:
    - Single Responsibility: Only handles command processing
    - Open/Closed: Easy to add new commands without modifying existing code
    - Dependency Inversion: Uses BA Knowledge Service abstraction
    """
    
    async def handle(self, command: str) -> None:
        """
        Main handler method for command processing.
        Routes commands to appropriate handler methods.
        
        Args:
            command: Command string to process
        """
        await self.handle_command(command)
    
    async def handle_command(self, command: str) -> None:
        """
        Route command to appropriate handler method.
        
        Args:
            command: Command string to process
        """
        if command == Commands.ADD_FILE_SOURCE["id"]:
            await self.handle_add_file_source()
        elif command == Commands.MANAGER_FILE_SOURCE["id"]:
            await self.handle_manager_file_source()
        elif command == Commands.CLEAR_KNOWLEDGE_GRAPH["id"]:
            await self.handle_clear_knowledge_graph()
        else:
            error_msg = UIMessages.UNKNOWN_COMMAND_ERROR.format(command=command)
            await self.send_error_message(error_msg)
    
    async def handle_add_file_source(self) -> None:
        """
        Handle 'Add File Source' command.
        Delegates to FileHandler for file upload functionality.
        """
        # Import FileHandler here to avoid circular imports
        from .file_handler import FileHandler
        file_handler = FileHandler(self.factory)
        await file_handler.ask_file_source()
    
    async def handle_manager_file_source(self) -> None:
        """
        Handle 'Manager File Source' command.
        Currently shows coming soon message - ready for future implementation.
        """
        message = ResponseFormatter.format_feature_coming_soon("File source management")
        await self.send_message(message)
    
    async def handle_clear_knowledge_graph(self) -> None:
        """
        Handle 'Clear knowledge graph' command.
        
        - Clears the knowledge graph using BA knowledge service
        - Shows success/error message
        - Triggers file upload request after successful clear
        """
        # Clear the knowledge graph
        result = await self.ba_knowledge.clear_business_knowledge()
        
        if result.get("status") == "success":
            success_message = ResponseFormatter.format_clear_success()
            await self.send_message(success_message)
            
            # Ask for new file source after clearing
            await self.handle_add_file_source()
        else:
            error_msg = result.get("message", "Unknown error occurred")
            error_message = UIMessages.CLEAR_KNOWLEDGE_GRAPH_ERROR.format(message=error_msg)
            await self.send_error_message(error_message)
    
    def get_supported_commands(self) -> list[str]:
        """
        Get list of supported command strings.
        Useful for validation and documentation.
        
        Returns:
            List of supported command strings
        """
        return [
            Commands.ADD_FILE_SOURCE["id"],
            Commands.MANAGER_FILE_SOURCE["id"], 
            Commands.CLEAR_KNOWLEDGE_GRAPH["id"]
        ]
    
    async def add_custom_command_handler(self, command: str, handler_func) -> None:
        """
        Add custom command handler for extensibility.
        Future use for LangGraph agent integration or custom commands.
        
        Args:
            command: Command string to handle
            handler_func: Async function to handle the command
        """
        # This method provides extensibility for future command additions
        # Implementation would involve a command registry pattern
        pass
