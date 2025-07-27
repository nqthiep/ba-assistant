"""
UI Constants and String Literals
Centralizes all string literals used across the Chainlit UI handlers.
Improves maintainability and prepares for future i18n support.
"""

from typing import List, Dict, Any


class UIMessages:
    """UI message constants for consistent messaging across handlers."""
    
    # Welcome Messages
    WELCOME_TITLE = "### Welcome to BA Assistant: Trợ lý thông minh cho dự án phần mềm của bạn"
    WELCOME_DESCRIPTION = """BA Assistant là công cụ mạnh mẽ giúp nhóm dự án phần mềm quản lý và truy cập thông tin hiệu quả. Nó chuyển đổi tài liệu dự án thành nguồn tri thức tương tác."""
    
    WELCOME_FEATURES = """## Tính năng chính:  
- **Xử lý tài liệu**: Tiếp nhận, xử lý đa dạng tài liệu dự án (yêu cầu, thiết kế).  
- **Tạo Knowledge Graph**: Xây dựng bản đồ tri thức chi tiết, liên kết thông tin.  
- **Trò chuyện thông minh**: Tương tác trực tiếp qua giao diện, nhận câu trả lời chính xác từ tri thức dự án.  
- **Tăng hiệu quả**: Cung cấp truy cập thông tin tức thì, giảm thời gian tìm kiếm, hỗ trợ ra quyết định."""
    
    @classmethod
    def get_welcome_message(cls) -> str:
        """Get complete welcome message."""
        return f"{cls.WELCOME_TITLE}\n{cls.WELCOME_DESCRIPTION}\n\n{cls.WELCOME_FEATURES}"
    
    # File Processing Messages
    FILE_UPLOAD_REQUEST = "Please upload files to begin build knowledge graph!"
    FILE_PROCESSING_START = "I received the following files:\n{file_list}\n\nPlease wait for the system to build knowledge graph..."
    
    # Success Messages
    DOCUMENTS_PROCESSED_SUCCESS = "✅ **Documents processed successfully!**"
    KNOWLEDGE_GRAPH_CLEARED = "✅ Knowledge graph has been cleared successfully!"
    KNOWLEDGE_GRAPH_INITIALIZED = "Knowledge graph has been built successfully!"
    
    # Error Messages
    DOCUMENTS_PROCESSING_ERROR = "❌ **Error processing documents:**"
    INITIALIZATION_FAILED = "Failed to initialize: {message}"
    UNKNOWN_COMMAND_ERROR = "Unknown command: {command}"
    CLEAR_KNOWLEDGE_GRAPH_ERROR = "Failed to clear knowledge graph: {message}"
    
    # Search Messages
    SEARCH_RESULT_PREFIX = "Here is the search result:\n"
    
    # Agent Messages
    AGENT_NOT_IMPLEMENTED = "🤖 **Agent Processing**\n\nLangGraph agent integration is not yet implemented.\n\nThis handler is prepared for future agent-based workflows including:\n- Multi-step reasoning\n- Tool usage coordination\n- Knowledge graph integration\n- Contextual conversation handling"
    
    # Feature Coming Soon
    FEATURE_COMING_SOON = "{feature_name} feature coming soon!"
    
    # Summary Formatting
    SUMMARY_HEADER = "📊 **Summary:**"
    CATEGORY_HEADER = "📂 **By Category:**"


class Commands:
    """Command definitions for Chainlit UI."""
    
    ADD_FILE_SOURCE = {
        "id": "Add File Source",
        "icon": "file-plus", 
        "description": "Add new file source",
        "button": True
    }
    
    MANAGER_FILE_SOURCE = {
        "id": "Manager File Source",
        "icon": "folder-kanban",
        "description": "Manager file source", 
        "button": True
    }
    
    CLEAR_KNOWLEDGE_GRAPH = {
        "id": "Clear knowledge graph",
        "icon": "trash",
        "description": "Clear knowledge graph",
        "button": True
    }
    
    @classmethod
    def get_all_commands(cls) -> List[Dict[str, Any]]:
        """Get all available commands."""
        return [
            cls.ADD_FILE_SOURCE,
            cls.MANAGER_FILE_SOURCE,
            cls.CLEAR_KNOWLEDGE_GRAPH
        ]


class FileTypes:
    """Supported file types and MIME type definitions."""
    
    # Document file types
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # Spreadsheet file types
    XLS = "application/vnd.ms-excel"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Text file types
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    PDF = "application/pdf"
    PLAIN_TEXT = "text/plain"
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported MIME types."""
        return [
            cls.DOC,
            cls.DOCX,
            cls.XLS,
            cls.XLSX,
            cls.MARKDOWN,
            cls.HTML,
            cls.PDF,
            cls.PLAIN_TEXT
        ]


class FileSettings:
    """File upload settings and limits."""
    
    MAX_SIZE_MB = 10
    MAX_FILES = 10


class DebugMessages:
    """Debug and logging message constants."""
    
    # Initialization messages
    ORCHESTRATOR_INIT_START = "[DEBUG] Initializing ChainlitOrchestrator..."
    ORCHESTRATOR_INIT_SUCCESS = "[DEBUG] ChainlitOrchestrator initialized successfully"
    ORCHESTRATOR_INIT_ERROR = "[ERROR] Failed to initialize ChainlitOrchestrator: {error}"
    
    # Event handling messages
    CHAT_START_TRIGGERED = "[DEBUG] on_chat_start triggered!"
    CHAT_START_SUCCESS = "[DEBUG] orchestrator.on_chat_start() completed successfully"
    CHAT_START_ERROR = "[ERROR] Error in orchestrator.on_chat_start(): {error}"
    
    MESSAGE_TRIGGERED = "[DEBUG] on_message triggered with: {content}"
    MESSAGE_SUCCESS = "[DEBUG] orchestrator.on_message() completed successfully"
    MESSAGE_ERROR = "[ERROR] Error in orchestrator.on_message(): {error}"
    
    # Handler messages
    HANDLERS_REFACTORED_INFO = "[INFO] ChainlitHandlers is using the new refactored architecture."
    HANDLERS_DELEGATING_INFO = "[INFO] Delegating to ChainlitOrchestrator and specialized handlers."
    
    # Deprecation messages
    DEPRECATED_HANDLERS = "[DEPRECATED] ChainlitHandlers is deprecated. Use ChainlitOrchestrator instead."
    DEPRECATED_CHAT_START = "[DEPRECATED] ChainlitHandlers.on_chat_start() is deprecated. Use ChainlitOrchestrator instead."
    DEPRECATED_MESSAGE = "[DEPRECATED] ChainlitHandlers.on_message() is deprecated. Use ChainlitOrchestrator instead."


class AgentWorkflows:
    """Future agent workflow definitions."""
    
    DOCUMENT_ANALYSIS = "document_analysis"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    QUESTION_ANSWERING = "question_answering"
    MULTI_STEP_REASONING = "multi_step_reasoning"
    
    @classmethod
    def get_available_workflows(cls) -> List[str]:
        """Get list of available workflow names."""
        return [
            cls.DOCUMENT_ANALYSIS,
            cls.KNOWLEDGE_EXTRACTION,
            cls.QUESTION_ANSWERING,
            cls.MULTI_STEP_REASONING
        ]


class StatusMessages:
    """Status and state messages."""
    
    NOT_IMPLEMENTED = "not_implemented"
    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"
    DONE = "done"
    
    # Status descriptions
    NOT_IMPLEMENTED_MSG = "Feature not yet implemented"
    WORKFLOW_NOT_IMPLEMENTED = "Workflow execution not yet implemented"
    ACTION_NOT_IMPLEMENTED = "Agent action handling not yet implemented"
