"""
BA Assistant - Chainlit Entry Point
This file initializes and runs the Chainlit app for the BA Assistant project.
"""

import chainlit as cl
import os
from dotenv import load_dotenv
from markitdown import MarkItDown
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig  
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig  
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient  

# Initialize Graphiti client
GRAPHITI_API_KEY = os.getenv("GOOGLE_API_KEY")  # Ensure you have this in your .env file
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "Kim@cuong2",
    llm_client=GeminiClient(
        config=LLMConfig(
            api_key=GRAPHITI_API_KEY,
            model="gemini-2.0-flash"
        )
    ),
    embedder=GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=GRAPHITI_API_KEY,
            embedding_model="embedding-001"
        )
    ),
    cross_encoder=GeminiRerankerClient(
        config=LLMConfig(
            api_key=GRAPHITI_API_KEY,
            model="gemini-2.5-flash-lite-preview-06-17"
        )
    )
)


# Load environment variables from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from database.redis_manager import RedisGroupManager
from datetime import datetime

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

llm_transformer = LLMGraphTransformer(llm=llm)

group_manager = RedisGroupManager()
project_id = "BA_Project_001"

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
            content="Please upload files to begin building the knowledge graph!", accept=[
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
                content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build the knowledge graph..."
            ).send()

            md = MarkItDown(enable_plugins=True) # Set to True to enable plugins
            for file in files:
                # Process each file and send to Graphiti
                result = md.convert(file.path)
                document_content = result.text_content
                
                file_hash = group_manager.hash_file(file.path)

                group_id, is_existing = group_manager.get_or_create_group_id(
                    project_id=project_id,
                    filename=file.name,
                    file_path=file.path
                )
                
                group_id = group_id.replace(".", "_")
                if is_existing:
                    
                    await graphiti.add_episode(
                        name=file.name,
                        episode_body=document_content,
                        group_id=group_id,
                        reference_time=datetime.now().isoformat(),
                        source_description='Description of source'
                    )
                    group_manager.update_latest_version(project_id, file.name, file_hash, group_id)
                    await cl.Message(content=f"🔁 Document `{file.name}` updated in graph `{group_id}`.").send()
                
                else:
                    # First time creation
                    await graphiti.add_episode(
                        name=file.name,
                        episode_body=document_content,
                        group_id=group_id,
                        reference_time=datetime.now().isoformat(),
                        source_description='Description of source'
                    )
                    group_manager.update_latest_version(project_id, file.name, file_hash, group_id)
                    await cl.Message(content=f"🆕 New episode created in group `{group_id}`.").send()