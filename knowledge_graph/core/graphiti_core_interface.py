"""
Core Graphiti Interface
Layer 1 - Direct interactions with Graphiti's specific methods.
This layer isolates all direct Graphiti API calls for maximum flexibility.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode


class GraphitiCoreInterface(ABC):
    """
    Abstract interface for core Graphiti operations.
    Defines the contract for direct Graphiti API interactions.
    This is Layer 1 - the lowest level that directly interacts with Graphiti.
    """
    
    @abstractmethod
    async def search_graph(self, query: str) -> List[Any]:
        """
        Perform a search query on the knowledge graph.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results from Graphiti
        """
        pass
    
    @abstractmethod
    async def add_single_episode(
        self, 
        name: str, 
        content: str, 
        source: EpisodeType,
        source_description: str,
        reference_time: datetime,
        update_communities: bool = True
    ) -> Any:
        """
        Add a single episode to the knowledge graph.
        
        Args:
            name: Episode name
            content: Episode content
            source: Episode source type
            source_description: Description of the source
            reference_time: Reference time for the episode
            update_communities: Whether to update communities
            
        Returns:
            Episode creation result from Graphiti
        """
        pass
    
    @abstractmethod
    async def add_bulk_episodes(self, episodes: List[RawEpisode]) -> List[Any]:
        """
        Add multiple episodes to the knowledge graph in bulk.
        
        Args:
            episodes: List of RawEpisode objects
            
        Returns:
            List of episode creation results from Graphiti
        """
        pass
    
    @abstractmethod
    async def clear_all_data(self) -> None:
        """Clear all data from the knowledge graph."""
        pass
    
    @abstractmethod
    async def retrieve_episodes(
        self, 
        reference_time: datetime, 
        last_n: int = 1
    ) -> List[Any]:
        """
        Retrieve episodes from the knowledge graph.
        
        Args:
            reference_time: Reference time for episode retrieval
            last_n: Number of last episodes to retrieve
            
        Returns:
            List of episodes from Graphiti
        """
        pass
    
    @abstractmethod
    async def verify_connection(self) -> None:
        """Verify database connectivity."""
        pass
    
    @abstractmethod
    async def build_indices_and_constraints(self) -> None:
        """Build database indices and constraints."""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the Graphiti instance is properly initialized."""
        pass
