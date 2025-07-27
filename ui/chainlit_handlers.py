"""
Chainlit UI Handlers
Handles all Chainlit-specific UI interactions and event handlers.
Follows Single Responsibility Principle - only manages UI interactions.
Uses Layer 3 (BA Knowledge Service) directly for clean architecture.
"""

import chainlit as cl
from typing import List, Tuple, Any
from knowledge_graph import KnowledgeGraphFactory
# from utils.file_receiver import on_file_receiver  # Replaced by new pipeline


class ChainlitHandlers:
    """
    Manages Chainlit UI event handlers and user interactions.
    Uses Layer 3 (BA Knowledge Service) directly for clean 3-layer architecture.
    """
    
    def __init__(self):
        self.factory = KnowledgeGraphFactory()
        self.ba_knowledge = self.factory.get_ba_knowledge_service()
        self.commands = [
            {"id": "Add File Source", "icon": "file-plus", "description": "Add new file source", "button": True},
            {"id": "Manager File Source", "icon": "folder-kanban", "description": "Manager file source", "button": True},
            {"id": "Clear knowledge graph", "icon": "trash", "description": "Clear knowledge graph", "button": True},
        ]
    
    async def on_chat_start(self) -> None:
        """Handle chat start event."""
        await cl.context.emitter.set_commands(self.commands)
        status = await self.ba_knowledge.get_knowledge_status()
        
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
            # Use Layer 3 (BA Knowledge Service) instead of direct GraphitiClient
            init_result = await self.ba_knowledge.initialize_knowledge_system()
            if init_result.get("status") == "success":
                await self._ask_file_source()
                await cl.Message(content="Knowledge graph has been built successfully!").send()
            else:
                await cl.Message(content=f"Failed to initialize: {init_result.get('message')}").send()
    
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
        # Use Layer 3 for business knowledge search with formatting
        formatted_result = await self.ba_knowledge.search_business_knowledge(user_input)
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
            await self._process_uploaded_files_new_pipeline(files)
    
    async def _process_uploaded_files_new_pipeline(self, files: List[Any]) -> None:
        """
        Process uploaded files using the new Layer 2 pipeline.
        This replaces the old file_receiver + add_business_documents flow.
        """
        # Build list of file names for user notification
        file_names = [f"- {file.name if hasattr(file, 'name') else file.path}" for file in files]
        
        # Let the user know that the system is processing
        await cl.Message(
            content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
        ).send()
        
        # Process files using the new complete pipeline (Layer 3)
        result = await self.ba_knowledge.process_uploaded_files(files)
        
        # Send results to user using Layer 3 response format
        if result.get("status") == "success":
            summary = result.get("summary", {})
            by_category = result.get("by_category", {})
            
            content = f"✅ **Documents processed successfully!**\n\n"
            content += f"📊 **Summary:**\n"
            content += f"- Total files: {summary.get('total_files', 0)}\n"
            content += f"- Episodes created: {summary.get('total_episodes', 0)}\n"
            content += f"- Knowledge nodes: {summary.get('total_nodes', 0)}\n"
            content += f"- Relationships: {summary.get('total_edges', 0)}\n\n"
            
            content += f"📂 **By Category:**\n"
            for category, items in by_category.items():
                if items:
                    content += f"- {category.replace('_', ' ').title()}: {len(items)} sections\n"
            
            await cl.Message(content=content).send()
        else:
            error_content = f"❌ **Error processing documents:**\n\n"
            error_content += f"**Message:** {result.get('message', 'Unknown error')}\n\n"
            
            if result.get('error'):
                error_content += f"**Details:** {result.get('error')}\n\n"
            
            error_content += "Please check your files and try again."
            await cl.Message(content=error_content).send()
    
    async def _add_files_to_episodes(self, files: List[Tuple[str, str]]) -> None:
        """Add uploaded files to knowledge graph episodes."""
        # Build list of file names received
        file_names = [f"- {file_path}" for file_path, file_content in files]
        
        # Let the user know that the system is ready
        await cl.Message(
            content=f"I received the following files:\n{chr(10).join(file_names)}\n\nPlease wait for the system to build knowledge graph..."
        ).send()
        
        # Add files to knowledge graph using Layer 3
        result = await self.ba_knowledge.add_business_documents(files)
        
        # Send results to user using Layer 3 response format
        if result.get("status") == "success":
            summary = result.get("summary", {})
            by_category = result.get("by_category", {})
            
            content = f"✅ **Documents processed successfully!**\n\n"
            content += f"📊 **Summary:**\n"
            content += f"- Total documents: {summary.get('total_documents', 0)}\n"
            content += f"- Episodes created: {summary.get('total_episodes', 0)}\n"
            content += f"- Knowledge nodes: {summary.get('total_nodes', 0)}\n"
            content += f"- Relationships: {summary.get('total_edges', 0)}\n\n"
            
            content += f"📂 **By Category:**\n"
            for category, items in by_category.items():
                if items:
                    content += f"- {category.replace('_', ' ').title()}: {len(items)} sections\n"
            
            await cl.Message(content=content).send()
        else:
            error_msg = result.get("message", "Unknown error occurred")
            await cl.Message(content=f"❌ **Error processing documents:** {error_msg}").send()
    
    async def _clear_knowledge_graph(self) -> None:
        """Clear the knowledge graph using Layer 3."""
        result = await self.ba_knowledge.clear_business_knowledge()
        
        if result.get("status") == "success":
            await cl.Message(content="✅ Knowledge graph has been cleared successfully!").send()
        else:
            error_msg = result.get("message", "Unknown error occurred")
            await cl.Message(content=f"❌ **Error clearing knowledge:** {error_msg}").send()
