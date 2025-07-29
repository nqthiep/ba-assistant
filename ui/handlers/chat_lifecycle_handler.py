"""
Chat Lifecycle Handler for Chainlit UI
Handles chat initialization, welcome messages, and system setup.
Follows Single Responsibility Principle - only manages chat lifecycle.
"""

import os
import logging
import chainlit as cl
from typing import List, Dict, Any
from .base_handler import BaseChainlitHandler
from .response_formatter import ResponseFormatter
from ..constants import Commands

logger = logging.getLogger(__name__)


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
    
    # Class-level flag to track if graph setup has been completed
    _graph_setup_completed = False
    
    def __init__(self, factory):
        """
        Initialize chat lifecycle handler.
        
        Args:
            factory: KnowledgeGraphFactory for dependency injection
        """
        super().__init__(factory)
        self.commands = Commands.get_all_commands()
    
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
        
        # Verify system configuration
        await self._verify_system_configuration()
        
        # Always ensure indices and constraints are built for proper entity extraction
        await self._ensure_graph_setup()
        
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
    
    async def _ensure_graph_setup(self) -> None:
        """
        Ensure graph indices and constraints are properly set up.
        This is critical for entity extraction and relationship creation.
        Only runs once per application lifecycle.
        """
        # Check if setup has already been completed
        if ChatLifecycleHandler._graph_setup_completed:
            print("[DEBUG] Graph setup already completed, skipping...")
            return
            
        try:
            print("[DEBUG] Ensuring graph indices and constraints are built...")
            
            # Call initialize_knowledge_system which internally calls build_indices_and_constraints
            # This ensures the setup is done properly and only once
            init_result = await self.ba_knowledge.initialize_knowledge_system()
            
            if init_result.get("status") == "success":
                print("[DEBUG] Graph setup completed successfully")
            else:
                print(f"[DEBUG] Graph setup completed with status: {init_result.get('status')}")
            
            # Mark setup as completed regardless of status to prevent repeated attempts
            ChatLifecycleHandler._graph_setup_completed = True
            
        except Exception as e:
            print(f"[ERROR] Failed to setup graph indices and constraints: {e}")
            # Still mark as completed to prevent repeated failed attempts
            ChatLifecycleHandler._graph_setup_completed = True
            await self.send_message(f"⚠️ Warning: Graph setup failed. Entity extraction may not work properly: {str(e)}")
    
    async def _verify_system_configuration(self) -> None:
        """
        Verify that environment variables are loaded correctly and logging is configured.
        This helps debug system configuration issues.
        """
        logger.info("[CONFIG] Verifying system configuration...")
        
        # Check critical environment variables
        env_vars_to_check = [
            "NEO4J_URI",
            "NEO4J_USER", 
            "NEO4J_PASSWORD",
            "OPENAI_API_KEY",
            "DEFAULT_DATABASE"
        ]
        
        missing_vars = []
        for var in env_vars_to_check:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
                logger.error(f"[CONFIG] Missing environment variable: {var}")
            else:
                # Log partial value for security (don't log full API keys)
                if "KEY" in var or "PASSWORD" in var:
                    masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    logger.info(f"[CONFIG] ✅ {var}: {masked_value}")
                else:
                    logger.info(f"[CONFIG] ✅ {var}: {value}")
        
        # Check optional environment variables
        optional_vars = ["SEMAPHORE_LIMIT", "LLM_MODEL"]
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                logger.info(f"[CONFIG] ✅ {var}: {value}")
            else:
                logger.info(f"[CONFIG] ⚠️ Optional {var}: not set (using defaults)")
        
        # Verify logging configuration
        root_logger = logging.getLogger()
        logger.info(f"[CONFIG] ✅ Logging level: {logging.getLevelName(root_logger.level)}")
        logger.info(f"[CONFIG] ✅ Logging handlers: {len(root_logger.handlers)}")
        
        # Report configuration status
        if missing_vars:
            error_msg = f"❌ Missing critical environment variables: {', '.join(missing_vars)}"
            logger.error(f"[CONFIG] {error_msg}")
            await self.send_message(f"⚠️ Configuration Error: {error_msg}")
        else:
            logger.info("[CONFIG] ✅ All critical environment variables loaded successfully")
            await self.send_message("✅ System configuration verified successfully")
        
        # Test logging at different levels
        logger.debug("[CONFIG] Debug logging test")
        logger.info("[CONFIG] Info logging test")
        logger.warning("[CONFIG] Warning logging test")
        
        logger.info("[CONFIG] System configuration verification completed")
    
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
