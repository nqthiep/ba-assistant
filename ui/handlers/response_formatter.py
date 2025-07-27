"""
Response Formatter for Chainlit UI
Handles formatting of various types of responses and messages.
Follows Single Responsibility Principle - only handles response formatting.
"""

from typing import Dict, Any, List


class ResponseFormatter:
    """
    Utility class for formatting UI responses and messages.
    Provides consistent formatting across all handlers.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles response formatting
    - Open/Closed: Easy to extend with new formatting methods
    """
    
    @staticmethod
    def format_welcome_message() -> str:
        """
        Format the welcome message for chat start.
        
        Returns:
            Formatted welcome message string
        """
        content = """### Welcome to BA Assistant: Trợ lý thông minh cho dự án phần mềm của bạn   
BA Assistant là công cụ mạnh mẽ giúp nhóm dự án phần mềm quản lý và truy cập thông tin hiệu quả. Nó chuyển đổi tài liệu dự án thành nguồn tri thức tương tác.  

## Tính năng chính:  
- **Xử lý tài liệu**: Tiếp nhận, xử lý đa dạng tài liệu dự án (yêu cầu, thiết kế).  
- **Tạo Knowledge Graph**: Xây dựng bản đồ tri thức chi tiết, liên kết thông tin.  
- **Trò chuyện thông minh**: Tương tác trực tiếp qua giao diện, nhận câu trả lời chính xác từ tri thức dự án.  
- **Tăng hiệu quả**: Cung cấp truy cập thông tin tức thì, giảm thời gian tìm kiếm, hỗ trợ ra quyết định.
"""
        return content
    
    @staticmethod
    def format_file_processing_start(file_names: List[str]) -> str:
        """
        Format message when file processing starts.
        
        Args:
            file_names: List of file names being processed
            
        Returns:
            Formatted processing start message
        """
        file_list = "\n".join([f"- {name}" for name in file_names])
        return f"I received the following files:\n{file_list}\n\nPlease wait for the system to build knowledge graph..."
    
    @staticmethod
    def format_processing_success(result: Dict[str, Any]) -> str:
        """
        Format successful processing result message.
        
        Args:
            result: Processing result dictionary with summary and category data
            
        Returns:
            Formatted success message
        """
        summary = result.get("summary", {})
        by_category = result.get("by_category", {})
        
        content = "✅ **Documents processed successfully!**\n\n"
        content += "📊 **Summary:**\n"
        content += f"- Total files: {summary.get('total_files', 0)}\n"
        content += f"- Episodes created: {summary.get('total_episodes', 0)}\n"
        content += f"- Knowledge nodes: {summary.get('total_nodes', 0)}\n"
        content += f"- Relationships: {summary.get('total_edges', 0)}\n\n"
        
        content += "📂 **By Category:**\n"
        for category, items in by_category.items():
            if items:
                content += f"- {category.replace('_', ' ').title()}: {len(items)} sections\n"
        
        return content
    
    @staticmethod
    def format_processing_error(result: Dict[str, Any]) -> str:
        """
        Format error processing result message.
        
        Args:
            result: Error result dictionary with message and error details
            
        Returns:
            Formatted error message
        """
        error_content = "❌ **Error processing documents:**\n\n"
        error_content += f"**Message:** {result.get('message', 'Unknown error')}\n\n"
        
        if result.get('error'):
            error_content += f"**Details:** {result.get('error')}\n\n"
        
        error_content += "Please check your files and try again."
        return error_content
    
    @staticmethod
    def format_search_result(formatted_result: str) -> str:
        """
        Format search result message.
        
        Args:
            formatted_result: Pre-formatted search result from BA knowledge service
            
        Returns:
            Formatted search result message
        """
        return f"Here is the search result:\n{formatted_result}"
    
    @staticmethod
    def format_clear_success() -> str:
        """
        Format successful knowledge graph clear message.
        
        Returns:
            Formatted clear success message
        """
        return "✅ Knowledge graph has been cleared successfully!"
    
    @staticmethod
    def format_initialization_success() -> str:
        """
        Format successful knowledge graph initialization message.
        
        Returns:
            Formatted initialization success message
        """
        return "Knowledge graph has been built successfully!"
    
    @staticmethod
    def format_initialization_error(result: Dict[str, Any]) -> str:
        """
        Format knowledge graph initialization error message.
        
        Args:
            result: Initialization result with error details
            
        Returns:
            Formatted initialization error message
        """
        return f"Failed to initialize: {result.get('message', 'Unknown error')}"
    
    @staticmethod
    def format_feature_coming_soon(feature_name: str) -> str:
        """
        Format coming soon message for features under development.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Formatted coming soon message
        """
        return f"{feature_name} feature coming soon!"
