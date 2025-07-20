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

from graphiti_core.nodes import EpisodeType
# from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
# from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
# from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

# llm_client = GeminiClient(config=LLMConfig(model="gemini-2.0-flash"))
# embedder = GeminiEmbedder(config=GeminiEmbedderConfig(embedding_model="embedding-001"))
# cross_encoder = GeminiRerankerClient(config=LLMConfig(model="gemini-2.5-flash-lite-preview-06-17"))


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
    # llm_client=llm_client,
    # embedder=embedder,
    # cross_encoder=cross_encoder
)

commands = [
    {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
    {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True},
    {"id": "Clear knowledge graph", "icon": "trash", "description": "Clear knowledge graph", "button": True},
]

@cl.on_chat_start
async def start():
    await cl.context.emitter.set_commands(commands)
    status = await check_graphiti_status(graphiti) 

    content = """### Welcome to BA Assistant: Trợ lý thông minh cho dự án phần mềm của bạn   
BA Assistant là công cụ mạnh mẽ giúp nhóm dự án phần mềm quản lý và truy cập thông tin hiệu quả. Nó chuyển đổi tài liệu dự án thành nguồn tri thức tương tác.  
## Tính năng chính:  
- **Xử lý tài liệu**: Tiếp nhận, xử lý đa dạng tài liệu dự án (yêu cầu, thiết kế).  
- **Tạo Knowledge Graph**: Xây dựng bản đồ tri thức chi tiết, liên kết thông tin.  
- **Trò chuyện thông minh**: Tương tác trực tiếp qua giao diện, nhận câu trả lời chính xác từ tri thức dự án.  
- **Tăng hiệu quả**: Cung cấp truy cập thông tin tức thì, giảm thời gian tìm kiếm, hỗ trợ ra quyết định.
"""  
  
    await cl.Message(content=content).send()
    print(status)

    if (status["has_data"] == False):
        await graphiti.build_indices_and_constraints()
        await ask_file_source()
        await cl.Message(content="Knowledge graph has been built successfully!").send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages and respond accordingly.
    This is a placeholder logic. Integrate with your BA agent here.
    """

    if message.command:
        if message.command == "Add File Source":
            await ask_file_source()
        elif message.command == "Manager File Source":
            pass
        elif message.command == "Clear knowledge graph":
            await clear_knowledge_graph()
    else:
        user_input = message.content

        search_result = await graphiti.search(user_input)
        await print_facts(search_result)

async def clear_knowledge_graph():
    from graphiti_core.utils.maintenance.graph_data_operations import clear_data   
    await clear_data(graphiti.driver)  
    await cl.Message(content="Knowledge graph has been cleared successfully!").send()

async def ask_file_source():
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
        await add_files_to_eposide(files)

async def add_files_to_eposide(files):
    # Build list file names received
    file_names = [f"- {file_path}" for file_path, file_content in files]
    # Let the user know that the system is ready
    await cl.Message(
        content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
    ).send()

    for file_path, file_content in files:
        result = await graphiti.add_episode(
            name="test",
            episode_body=file_content,
            source=EpisodeType.text,
            source_description="This is a description content.",
            reference_time=datetime.now(timezone.utc),
        )

        if result:  
            print(f"Episode created: {result.episode.uuid}")  
            print(f"Nodes created: {len(result.nodes)}")  
            print(f"Edges created: {len(result.edges)}")

        await cl.Message(
            content=f"Episode created: {result.episode.uuid}\nNodes created: {len(result.nodes)}\nEdges created: {len(result.edges)}"
        ).send()

async def print_facts(edges):
    search_result = "\n".join([edge.fact for edge in edges])
    await cl.Message(content="Here is the search result:\n" + search_result).send()

async def check_graphiti_status(graphiti):  
    """Kiểm tra trạng thái Graphiti và trả về dict"""   
      
    # Kiểm tra khởi tạo cơ bản  
    if not hasattr(graphiti, 'driver') or not graphiti.driver:  
        return {"status": "error", "message": "Driver not initialized"}  
      
    # Kiểm tra kết nối database  
    try:  
        await graphiti.driver.client.verify_connectivity()  
    except Exception as e:  
        return {"status": "error", "message": f"Database connection failed: {e}"}  
      
    # Kiểm tra có dữ liệu  
    try:  
        from graphiti_core.utils.maintenance.graph_data_operations import retrieve_episodes  
        from datetime import datetime, timezone  
        episodes = await retrieve_episodes(  
            graphiti.driver,  
            reference_time=datetime.now(timezone.utc),  
            last_n=1  
        )  
          
        return {  
            "status": "ok",  
            "message": "Graphiti is ready",  
            "has_data": len(episodes) > 0,  
            "episodes_count": len(episodes)  
        }  
    except Exception as e:  
        return {"status": "error", "message": f"Data check failed: {e}"}

if __name__ == "__main__":
    cl.run()
