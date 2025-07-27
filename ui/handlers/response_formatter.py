"""
Response Formatter for Chainlit UI
Handles formatting of various types of responses and messages.
Follows Single Responsibility Principle - only handles response formatting.
"""

from typing import Dict, Any, List
from ..constants import UIMessages


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
        return UIMessages.get_welcome_message()
    
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
        return UIMessages.FILE_PROCESSING_START.format(file_list=file_list)
    
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
        
        content = f"{UIMessages.DOCUMENTS_PROCESSED_SUCCESS}\n\n"
        content += f"{UIMessages.SUMMARY_HEADER}\n"
        content += f"- Total files: {summary.get('total_files', 0)}\n"
        content += f"- Episodes created: {summary.get('total_episodes', 0)}\n"
        content += f"- Knowledge nodes: {summary.get('total_nodes', 0)}\n"
        content += f"- Relationships: {summary.get('total_edges', 0)}\n\n"
        
        content += f"{UIMessages.CATEGORY_HEADER}\n"
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
        error_content = f"{UIMessages.DOCUMENTS_PROCESSING_ERROR}\n\n"
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
        return f"{UIMessages.SEARCH_RESULT_PREFIX}{formatted_result}"
    
    @staticmethod
    def format_clear_success() -> str:
        """
        Format successful knowledge graph clear message.
        
        Returns:
            Formatted clear success message
        """
        return UIMessages.KNOWLEDGE_GRAPH_CLEARED
    
    @staticmethod
    def format_initialization_success() -> str:
        """
        Format successful knowledge graph initialization message.
        
        Returns:
            Formatted initialization success message
        """
        return UIMessages.KNOWLEDGE_GRAPH_INITIALIZED
    
    @staticmethod
    def format_initialization_error(result: Dict[str, Any]) -> str:
        """
        Format knowledge graph initialization error message.
        
        Args:
            result: Initialization result with error details
            
        Returns:
            Formatted initialization error message
        """
        return UIMessages.INITIALIZATION_FAILED.format(message=result.get('message', 'Unknown error'))
    
    @staticmethod
    def format_feature_coming_soon(feature_name: str) -> str:
        """
        Format coming soon message for features under development.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Formatted coming soon message
        """
        return UIMessages.FEATURE_COMING_SOON.format(feature_name=feature_name)
