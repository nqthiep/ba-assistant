"""
BA Knowledge Interface
Layer 3 - Project-specific interfaces for the BA Assistant application.
This layer implements business logic specific to the BA Assistant project.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple


class BAKnowledgeInterface(ABC):
    """
    Abstract interface for BA Assistant knowledge operations.
    Layer 3 - Defines the contract for project-specific knowledge graph operations.
    """
    
    @abstractmethod
    async def search_business_knowledge(self, query: str) -> str:
        """
        Search business knowledge and format results for BA Assistant UI.
        
        Args:
            query: Business-related search query
            
        Returns:
            Formatted search results string for display
        """
        pass
    
    @abstractmethod
    async def add_business_documents(
        self, 
        documents: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Add business documents to the knowledge graph.
        Handles requirements, design docs, user manuals, etc.
        
        Args:
            documents: List of tuples containing (document_path, document_content)
            
        Returns:
            Summary of document processing results
        """
        pass
    
    @abstractmethod
    async def add_requirement_document(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Add a business requirement document to the knowledge graph.
        
        Args:
            file_path: Path to the requirement document
            content: Content of the requirement document
            
        Returns:
            Processing result summary
        """
        pass
    
    @abstractmethod
    async def add_design_document(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Add a design document to the knowledge graph.
        
        Args:
            file_path: Path to the design document
            content: Content of the design document
            
        Returns:
            Processing result summary
        """
        pass
    
    @abstractmethod
    async def add_user_manual(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Add a user manual to the knowledge graph.
        
        Args:
            file_path: Path to the user manual
            content: Content of the user manual
            
        Returns:
            Processing result summary
        """
        pass
    
    @abstractmethod
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """
        Get the status of the BA Assistant knowledge graph.
        
        Returns:
            Comprehensive status information for the UI
        """
        pass
    
    @abstractmethod
    async def clear_business_knowledge(self) -> Dict[str, Any]:
        """
        Clear all business knowledge from the graph.
        
        Returns:
            Operation result summary
        """
        pass
    
    @abstractmethod
    async def initialize_knowledge_system(self) -> Dict[str, Any]:
        """
        Initialize the knowledge system for BA Assistant.
        Sets up indices, constraints, and initial configuration.
        
        Returns:
            Initialization result summary
        """
        pass
    
    @abstractmethod
    async def get_document_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all documents in the knowledge graph.
        
        Returns:
            Summary of document types, counts, and metadata
        """
        pass
    
    @abstractmethod
    async def search_by_document_type(
        self, 
        document_type: str, 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search for content by document type (requirements, design, manual).
        
        Args:
            document_type: Type of document to search in
            query: Optional search query within that document type
            
        Returns:
            List of matching results with metadata
        """
        pass
