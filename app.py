"""
BA Assistant - Chainlit Entry Point
This file initializes and runs the Chainlit app for the BA Assistant project.
"""

import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)


@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages and respond accordingly.
    This is a placeholder logic. Integrate with your BA agent here.
    """
    user_input = message.content
    # TODO: Call BA agent logic here (e.g., agents/ba_agent.py)
    response = f"Bạn vừa gửi: {user_input}\n(Chức năng BA Assistant sẽ được tích hợp ở đây.)"
    await cl.Message(content=response).send()

if __name__ == "__main__":
    cl.run()
