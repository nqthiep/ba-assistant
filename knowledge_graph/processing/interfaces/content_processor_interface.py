"""
Content Processor Interface
Layer 2 - Common methods for adding different types of content to the knowledge graph.
This layer abstracts content processing and uses Layer 1 for actual Graphiti operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Union
from datetime import datetime


class ContentProcessorInterface(ABC):
    """
    Abstract interface for content processing operations.
    Layer 2 - Defines the contract for common content addition methods.
    """
    
    @abstractmethod
    async def add_text_content(
        self, 
        text: str, 
        title: str, 
        source_description: str = "Text content"
    ) -> Dict[str, Any]:
        """
        Add text content as an episode to the knowledge graph.
        
        Args:
            text: Text content to add
            title: Title for the episode
            source_description: Description of the source
            
        Returns:
            Episode creation result with metadata
        """
        pass
    
    @abstractmethod
    async def add_file_content(
        self, 
        file_path: str, 
        file_content: str
    ) -> List[Dict[str, Any]]:
        """
        Add file content as episodes to the knowledge graph.
        Automatically parses the content into sections.
        
        Args:
            file_path: Path to the file
            file_content: Content of the file
            
        Returns:
            List of episode creation results with metadata
        """
        pass
    
    @abstractmethod
    async def add_multiple_files(
        self, 
        files: List[Tuple[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Add multiple files as episodes to the knowledge graph.
        Uses bulk processing for better performance.
        
        Args:
            files: List of tuples containing (file_path, file_content)
            
        Returns:
            List of episode creation results with metadata
        """
        pass
    
    @abstractmethod
    async def add_json_content(
        self, 
        json_data: Dict[str, Any], 
        title: str,
        source_description: str = "JSON data"
    ) -> Dict[str, Any]:
        """
        Add JSON data as an episode to the knowledge graph.
        
        Args:
            json_data: JSON data to add
            title: Title for the episode
            source_description: Description of the source
            
        Returns:
            Episode creation result with metadata
        """
        pass
    
    @abstractmethod
    async def add_structured_content(
        self, 
        content_items: List[Dict[str, Union[str, Dict]]]
    ) -> List[Dict[str, Any]]:
        """
        Add structured content items to the knowledge graph.
        Each item should have 'title', 'content', and optional 'metadata'.
        
        Args:
            content_items: List of structured content items
            
        Returns:
            List of episode creation results with metadata
        """
        pass
    
    @abstractmethod
    async def search_content(self, query: str) -> List[Any]:
        """
        Search for content in the knowledge graph.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    async def clear_all_content(self) -> None:
        """Clear all content from the knowledge graph."""
        pass
