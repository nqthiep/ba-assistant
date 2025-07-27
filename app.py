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
print("[DEBUG] Initializing ChainlitHandlers...")
try:
    handlers = ChainlitHandlers()
    print("[DEBUG] ChainlitHandlers initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize ChainlitHandlers: {e}")
    import traceback
    traceback.print_exc()
    raise

@cl.on_chat_start
async def start():
    """Handle chat start event by delegating to handlers."""
    print("[DEBUG] on_chat_start triggered!")
    try:
        await handlers.on_chat_start()
        print("[DEBUG] handlers.on_chat_start() completed successfully")
    except Exception as e:
        print(f"[ERROR] Error in handlers.on_chat_start(): {e}")
        import traceback
        traceback.print_exc()
        raise

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user messages by delegating to handlers."""
    print(f"[DEBUG] on_message triggered with: {message.content if message else 'None'}")
    try:
        await handlers.on_message(message)
        print("[DEBUG] handlers.on_message() completed successfully")
    except Exception as e:
        print(f"[ERROR] Error in handlers.on_message(): {e}")
        import traceback
        traceback.print_exc()
        raise

# All functionality has been moved to specialized modules following SOLID principles:
# - Database operations: database/graphiti_client.py
# - Knowledge graph operations: utils/kg_operations.py  
# - UI handlers: ui/chainlit_handlers.py

if __name__ == "__main__":
    cl.run()
