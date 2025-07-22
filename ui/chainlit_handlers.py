"""
Chainlit UI Handlers
Handles all Chainlit-specific UI interactions and event handlers.
Follows Single Responsibility Principle - only manages UI interactions.
"""

import chainlit as cl
from typing import List, Tuple
from utils.kg_operations import KnowledgeGraphOperations
from utils.file_receiver import on_file_receiver


class ChainlitHandlers:
    """
    Manages Chainlit UI event handlers and user interactions.
    Depends on KnowledgeGraphOperations abstraction (Dependency Inversion Principle).
    """
    
    def __init__(self):
        self.kg_operations = KnowledgeGraphOperations()
        self.commands = [
            {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
            {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True},
            {"id": "Clear knowledge graph", "icon": "trash", "description": "Clear knowledge graph", "button": True},
        ]
    
    async def on_chat_start(self) -> None:
        """Handle chat start event."""
        await cl.context.emitter.set_commands(self.commands)
        status = await self.kg_operations.check_status()
        
        content = """### Welcome to BA Assistant: Trợ lý thông minh cho dự án phần mềm của bạn   
BA Assistant là công cụ mạnh mẽ giúp nhóm dự án phần mềm quản lý và truy cập thông tin hiệu quả. Nó chuyển đổi tài liệu dự án thành nguồn tri thức tương tác.  
## Tính năng chính:  
- **Xử lý tài liệu**: Tiếp nhận, xử lý đa dạng tài liệu dự án (yêu cầu, thiết kế).  
- **Tạo Knowledge Graph**: Xây dựng bản đồ tri thức chi tiết, liên kết thông tin.  
- **Trò chuyện thông minh**: Tương tác trực tiếp qua giao diện, nhận câu trả lời chính xác từ tri thức dự án.  
- **Tăng hiệu quả**: Cung cấp truy cập thông tin tức thì, giảm thời gian tìm kiếm, hỗ trợ ra quyết định.
"""
        
        await cl.Message(content=content).send()
        print(f"Status: {status} and has data: {status.get('has_data', False)}")
        
        if not status.get("has_data", False):
            from database.graphiti_client import GraphitiClient
            graphiti_client = GraphitiClient()
            await graphiti_client.build_indices_and_constraints()
            await self._ask_file_source()
            await cl.Message(content="Knowledge graph has been built successfully!").send()
    
    async def on_message(self, message: cl.Message) -> None:
        """Handle incoming user messages."""
        if message.command:
            await self._handle_command(message.command)
        else:
            await self._handle_user_query(message.content)
    
    async def _handle_command(self, command: str) -> None:
        """Handle command messages."""
        if command == "Add File Source":
            await self._ask_file_source()
        elif command == "Manager File Source":
            # TODO: Implement file source management
            await cl.Message(content="File source management feature coming soon!").send()
        elif command == "Clear knowledge graph":
            await self._clear_knowledge_graph()
            await self._ask_file_source()
    
    async def _handle_user_query(self, user_input: str) -> None:
        """Handle user query messages."""
        search_result = await self.kg_operations.search(user_input)
        formatted_result = self.kg_operations.format_search_results(search_result)
        await cl.Message(content="Here is the search result:\n" + formatted_result).send()
    
    async def _ask_file_source(self) -> None:
        """Ask user to upload files for knowledge graph building."""
        files = await cl.AskFileMessage(
            max_size_mb=10,
            max_files=10,
            content="Please upload files to begin build knowledge graph!",
            accept=[
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
            processed_files = await on_file_receiver(files)
            await self._add_files_to_episodes(processed_files)
    
    async def _add_files_to_episodes(self, files: List[Tuple[str, str]]) -> None:
        """Add uploaded files to knowledge graph episodes."""
        # Build list of file names received
        file_names = [f"- {file_path}" for file_path, file_content in files]
        
        # Let the user know that the system is ready
        await cl.Message(
            content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
        ).send()
        
        # Add files to knowledge graph
        results = await self.kg_operations.add_files_to_episodes(files)
        
        # Send results to user
        for result in results:
            await cl.Message(
                content=f"Episode created: {result['episode_uuid']}\nNodes created: {result['nodes_created']}\nEdges created: {result['edges_created']}"
            ).send()
    
    async def _clear_knowledge_graph(self) -> None:
        """Clear the knowledge graph."""
        await self.kg_operations.clear_knowledge_graph()
        await cl.Message(content="Knowledge graph has been cleared successfully!").send()
