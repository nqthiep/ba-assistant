"""
BA Assistant - Chainlit Entry Point
This file initializes and runs the Chainlit app for the BA Assistant project.
"""

import chainlit as cl
import os
from dotenv import load_dotenv
from utils.file_receiver import on_file_receiver

# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
from graphiti_core.nodes import EpisodeType

llm_client = GeminiClient(config=LLMConfig(model="gemini-2.0-flash"))
embedder = GeminiEmbedder(config=GeminiEmbedderConfig(embedding_model="embedding-001"))
cross_encoder = GeminiRerankerClient(config=LLMConfig(model="gemini-2.5-flash-lite-preview-06-17"))


from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from datetime import datetime, timezone

# Create a Neo4j driver with custom database name
driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678"
)

# Pass the driver to Graphiti
graphiti = Graphiti(
    graph_driver=driver, 
    llm_client=llm_client,
    embedder=embedder,
    cross_encoder=cross_encoder
)

commands = [
    {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
    {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True}
]

# Global variable to store uploaded files
global files
files = None

@cl.on_chat_start
async def start():
    await graphiti.build_indices_and_constraints()
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
    while files is None:
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
            files = await on_file_receiver(files)

            # Build list file names received
            file_names = [f"- {file_path}" for file_path, file_content in files]
            # Let the user know that the system is ready
            await cl.Message(
                content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
            ).send()

            for file_path, file_content in files:
                await graphiti.add_episode(
                    name=file_path,
                    episode_body=file_content,
                    source=EpisodeType.text,
                    source_description=file_content,
                    reference_time=datetime.now(timezone.utc),
                )

            await cl.Message(
                content="Knowledge graph has been built successfully!"
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
