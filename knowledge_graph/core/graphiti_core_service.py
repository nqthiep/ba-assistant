"""
Core Graphiti Service
Layer 1 - Concrete implementation of direct Graphiti API interactions.
Includes integrated connection management.
"""

import os
from datetime import datetime
from typing import List, Any, Optional
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode
from graphiti_core.utils.maintenance.graph_data_operations import clear_data, retrieve_episodes

from .graphiti_core_interface import GraphitiCoreInterface


class GraphitiCoreService(GraphitiCoreInterface):
    """
    Concrete implementation of core Graphiti operations.
    Layer 1 - Directly interacts with Graphiti's specific methods.
    Includes integrated connection management.
    Includes integrated connection management (formerly GraphitiClient).
    """
    
    _instance: Optional['GraphitiCoreService'] = None
    _graphiti: Optional[Graphiti] = None
    
    def __new__(cls) -> 'GraphitiCoreService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._graphiti is None:
            self._initialize_graphiti()
    
    def _initialize_graphiti(self) -> None:
        """Initialize Graphiti with Neo4j driver."""
        # Get connection details from environment variables
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_uri:
            raise ValueError('NEO4J_URI must be set in environment variables')
        if not neo4j_user:
            raise ValueError('NEO4J_USER must be set in environment variables')
        if not neo4j_password:
            raise ValueError('NEO4J_PASSWORD must be set in environment variables')

        # Create Neo4j driver
        driver = Neo4jDriver(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
        
        # Initialize Graphiti instance
        self._graphiti = Graphiti(graph_driver=driver)
    
    @property
    def graphiti(self) -> Graphiti:
        """Get the Graphiti instance."""
        if self._graphiti is None:
            self._initialize_graphiti()
        return self._graphiti
    
    async def search_graph(self, query: str) -> List[Any]:
        """Perform a search query on the knowledge graph."""
        return await self.graphiti.search(query)
    
    async def add_single_episode(
        self, 
        name: str, 
        content: str, 
        source: EpisodeType,
        source_description: str,
        reference_time: datetime,
        update_communities: bool = True
    ) -> Any:
        """Add a single episode to the knowledge graph."""
        return await self.graphiti.add_episode(
            name=name,
            episode_body=content,
            source=source,
            source_description=source_description,
            reference_time=reference_time,
            update_communities=update_communities
        )
    
    async def add_bulk_episodes(self, episodes: List[RawEpisode]) -> List[Any]:
        """Add multiple episodes to the knowledge graph in bulk with fallback to individual additions."""
        try:
            # Try bulk addition first
            # result = await self.graphiti.add_episode_bulk(episodes)
            results = []
            for episode in episodes:
                try:
                    individual_result = await self.graphiti.add_episode(
                        name=episode.name,
                        episode_body=episode.content,
                        source=episode.source,
                        source_description=episode.source_description,
                        reference_time=episode.reference_time,
                        update_communities=True
                    )
                    results.append(individual_result)
                except Exception as individual_error:
                    print(f"Failed to add individual episode '{episode.name}': {individual_error}")
                    # Continue with other episodes even if one fails
                    continue
            return results
        except Exception as e:
            # If bulk fails, fall back to individual additions
            print(f"Bulk episode addition failed in Graphiti API: {e}. Using individual additions.")
            
            results = []
            for episode in episodes:
                try:
                    individual_result = await self.graphiti.add_episode(
                        name=episode.name,
                        episode_body=episode.content,
                        source=episode.source,
                        source_description=episode.source_description,
                        reference_time=episode.reference_time,
                        update_communities=True
                    )
                    results.append(individual_result)
                except Exception as individual_error:
                    print(f"Failed to add individual episode '{episode.name}': {individual_error}")
                    # Continue with other episodes even if one fails
                    continue
            
            return results
    
    async def clear_all_data(self) -> None:
        """Clear all data from the knowledge graph."""
        await clear_data(self.graphiti.driver)
    
    async def retrieve_episodes(
        self, 
        reference_time: datetime, 
        last_n: int = 1
    ) -> List[Any]:
        """Retrieve episodes from the knowledge graph."""
        return await retrieve_episodes(
            self.graphiti.driver,
            reference_time=reference_time,
            last_n=last_n
        )
    
    async def verify_connection(self) -> None:
        """Verify database connectivity."""
        await self.graphiti.driver.client.verify_connectivity()
    
    async def build_indices_and_constraints(self) -> None:
        """Build database indices and constraints."""
        await self.graphiti.build_indices_and_constraints()
        await self.graphiti.build_communities()
    
    def is_initialized(self) -> bool:
        """Check if the Graphiti instance is properly initialized."""
        return (
            hasattr(self.graphiti, 'driver') and 
            self.graphiti.driver is not None
        )
