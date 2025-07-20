"""
BA Assistant - Chainlit Entry Point
This file serves as the main entry point for the Chainlit application.
Follows SOLID principles by delegating responsibilities to specialized modules.
"""

import chainlit as cl
import os
from dotenv import load_dotenv
from ui.chainlit_handlers import ChainlitHandlers

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

# Initialize the Chainlit handlers
handlers = ChainlitHandlers()

@cl.on_chat_start
async def start():
    """Handle chat start event by delegating to handlers."""
    await handlers.on_chat_start()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages by delegating to handlers."""
    await handlers.on_message(message)

# All functionality has been moved to specialized modules following SOLID principles:
# - Database operations: database/graphiti_client.py
# - Knowledge graph operations: utils/kg_operations.py  
# - UI handlers: ui/chainlit_handlers.py

if __name__ == "__main__":
    cl.run()
