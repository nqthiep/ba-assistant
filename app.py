"""
BA Assistant - Chainlit Entry Point
This file initializes and runs the Chainlit app for the BA Assistant project.
"""

import chainlit as cl
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)



commands = [
    {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
    {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True}
]

# Global variable to store uploaded files
global files
files = None

@cl.on_chat_start
async def start():
    await cl.context.emitter.set_commands(commands)

    content = """### Welcome to BA Assistant: Trợ lý thông minh cho dự án phần mềm của bạn   
BA Assistant là công cụ mạnh mẽ giúp nhóm dự án phần mềm quản lý và truy cập thông tin hiệu quả. Nó chuyển đổi tài liệu dự án thành nguồn tri thức tương tác.  
## Tính năng chính:  
- **Xử lý tài liệu**: Tiếp nhận, xử lý đa dạng tài liệu dự án (yêu cầu, thiết kế).  
- **Tạo Knowledge Graph**: Xây dựng bản đồ tri thức chi tiết, liên kết thông tin.  
- **Trò chuyện thông minh**: Tương tác trực tiếp qua giao diện, nhận câu trả lời chính xác từ tri thức dự án.  
- **Tăng hiệu quả**: Cung cấp truy cập thông tin tức thì, giảm thời gian tìm kiếm, hỗ trợ ra quyết định.
"""  
  
    await cl.Message(content=content).send()

    global files
    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            max_size_mb=10,
            max_files=10,
            content="Please upload files to begin build knowledge graph!", accept=[
                "application/msword",        # .doc
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
                "application/vnd.ms-excel",  # .xls
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
                "text/markdown",             # .md
                "text/html",                 # .html
                "application/pdf",           # .pdf
                "text/plain"                 # .txt
                ]
        ).send()

        if files:
            # Build list file names received
            file_names = [f"- {file.name}" for file in files]
            # Let the user know that the system is ready
            await cl.Message(
                content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
            ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages and respond accordingly.
    This is a placeholder logic. Integrate with your BA agent here.
    """

    if msg.command == "Add File Source":
        # User is using the Picture command
        pass

    user_input = message.content
    # TODO: Call BA agent logic here (e.g., agents/ba_agent.py)
    response = f"Bạn vừa gửi: {user_input}\n(Chức năng BA Assistant sẽ được tích hợp ở đây.)"
    await cl.Message(content=response).send()

if __name__ == "__main__":
    cl.run()
