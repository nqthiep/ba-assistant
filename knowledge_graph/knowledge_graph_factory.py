"""
Knowledge Graph Factory
Factory class to create and manage the 3-layer knowledge graph architecture.
Provides easy access to all layers with proper dependency injection.
"""

from knowledge_graph.core.graphiti_core_interface import GraphitiCoreInterface
from knowledge_graph.core.graphiti_core_service import GraphitiCoreService
from knowledge_graph.processing.content_processor_interface import ContentProcessorInterface
from knowledge_graph.processing.content_processor_service import ContentProcessorService
from knowledge_graph.business.ba_knowledge_interface import BAKnowledgeInterface
from knowledge_graph.business.ba_knowledge_service import BAKnowledgeService


class KnowledgeGraphFactory:
    """
    Factory class for creating and managing the 3-layer knowledge graph architecture.
    Ensures proper dependency injection and layer separation.
    
    Architecture:
    - Layer 1 (Core): Direct Graphiti API interactions
    - Layer 2 (Processing): Common content processing operations
    - Layer 3 (Business): BA Assistant specific business logic
    """
    
    _instance = None
    _core_service = None
    _content_processor = None
    _ba_knowledge_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_core_service(self) -> GraphitiCoreInterface:
        """
        Get Layer 1 (Core) - Direct Graphiti API interactions.
        
        Returns:
            GraphitiCoreInterface implementation
        """
        if self._core_service is None:
            self._core_service = GraphitiCoreService()
        return self._core_service
    
    def get_content_processor(self) -> ContentProcessorInterface:
        """
        Get Layer 2 (Processing) - Common content processing operations.
        
        Returns:
            ContentProcessorInterface implementation
        """
        if self._content_processor is None:
            self._content_processor = ContentProcessorService(self.get_core_service())
        return self._content_processor
    
    def get_ba_knowledge_service(self) -> BAKnowledgeInterface:
        """
        Get Layer 3 (Business) - BA Assistant specific operations.
        
        Returns:
            BAKnowledgeInterface implementation
        """
        if self._ba_knowledge_service is None:
            self._ba_knowledge_service = BAKnowledgeService(
                content_processor=self.get_content_processor(),
                core_service=self.get_core_service()
            )
        return self._ba_knowledge_service
    
    def create_custom_content_processor(self, core_service: GraphitiCoreInterface) -> ContentProcessorInterface:
        """
        Create a custom Layer 2 with a specific Layer 1 implementation.
        Useful for testing or alternative implementations.
        
        Args:
            core_service: Custom Layer 1 implementation
            
        Returns:
            ContentProcessorInterface implementation
        """
        return ContentProcessorService(core_service)
    
    def create_custom_ba_knowledge_service(
        self, 
        content_processor: ContentProcessorInterface, 
        core_service: GraphitiCoreInterface
    ) -> BAKnowledgeInterface:
        """
        Create a custom Layer 3 with specific Layer 1 and Layer 2 implementations.
        Useful for testing or alternative implementations.
        
        Args:
            content_processor: Custom Layer 2 implementation
            core_service: Custom Layer 1 implementation
            
        Returns:
            BAKnowledgeInterface implementation
        """
        return BAKnowledgeService(
            content_processor=content_processor,
            core_service=core_service
        )
    
    def reset_instances(self):
        """
        Reset all layer instances. Useful for testing or reconfiguration.
        """
        self._core_service = None
        self._content_processor = None
        self._ba_knowledge_service = None
