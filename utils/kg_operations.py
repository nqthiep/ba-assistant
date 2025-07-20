"""
Knowledge Graph Operations
Handles all knowledge graph related operations including search, episode management, and data operations.
Follows Single Responsibility Principle - only manages KG operations.
"""

from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.maintenance.graph_data_operations import clear_data, retrieve_episodes
from database.graphiti_client import GraphitiClient


class KnowledgeGraphOperations:
    """
    Handles all knowledge graph operations.
    Depends on GraphitiClient abstraction (Dependency Inversion Principle).
    """
    
    def __init__(self):
        self.graphiti_client = GraphitiClient()
    
    async def search(self, query: str) -> List[Any]:
        """Search the knowledge graph for relevant information."""
        return await self.graphiti_client.graphiti.search(query)
    
    async def add_episode(self, name: str, content: str, source_description: str = "Document content") -> Any:
        """
        Add a new episode to the knowledge graph.
        
        Args:
            name: Episode name
            content: Episode content
            source_description: Description of the source
            
        Returns:
            Episode creation result
        """
        return await self.graphiti_client.graphiti.add_episode(
            name=name,
            episode_body=content,
            source=EpisodeType.text,
            source_description=source_description,
            reference_time=datetime.now(timezone.utc),
        )
    
    async def add_files_to_episodes(self, files: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        Add multiple files as episodes to the knowledge graph.
        
        Args:
            files: List of tuples containing (file_path, file_content)
            
        Returns:
            List of episode creation results
        """
        results = []
        
        for file_path, file_content in files:
            result = await self.add_episode(
                name=f"Document: {file_path}",
                content=file_content,
                source_description=f"Content from file: {file_path}"
            )
            
            if result:
                episode_info = {
                    "file_path": file_path,
                    "episode_uuid": result.episode.uuid,
                    "nodes_created": len(result.nodes),
                    "edges_created": len(result.edges)
                }
                results.append(episode_info)
        
        return results
    
    async def clear_knowledge_graph(self) -> None:
        """Clear all data from the knowledge graph."""
        await clear_data(self.graphiti_client.graphiti.driver)
    
    async def check_status(self) -> Dict[str, Any]:
        """
        Check the status of the knowledge graph.
        
        Returns:
            Dictionary containing status information
        """
        # Check basic initialization
        if not hasattr(self.graphiti_client.graphiti, 'driver') or not self.graphiti_client.graphiti.driver:
            return {"status": "error", "message": "Driver not initialized"}
        
        # Check database connection
        try:
            await self.graphiti_client.verify_connection()
        except Exception as e:
            return {"status": "error", "message": f"Database connection failed: {e}"}
        
        # Check for existing data
        try:
            episodes = await retrieve_episodes(
                self.graphiti_client.graphiti.driver,
                reference_time=datetime.now(timezone.utc),
                last_n=1
            )
            
            return {
                "status": "ok",
                "message": "Graphiti is ready",
                "has_data": len(episodes) > 0,
                "episodes_count": len(episodes)
            }
        except Exception as e:
            return {"status": "error", "message": f"Data check failed: {e}"}
    
    def format_search_results(self, edges: List[Any]) -> str:
        """
        Format search results for display.
        
        Args:
            edges: List of search result edges
            
        Returns:
            Formatted search results string
        """
        if not edges:
            return "No results found."
        
        return "\n".join([edge.fact for edge in edges])
