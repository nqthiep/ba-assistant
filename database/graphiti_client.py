"""
Graphiti Database Client
Handles Neo4j driver initialization and Graphiti instance management.
Follows Single Responsibility Principle - only manages database connections.
"""

import os
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver
from typing import Optional


class GraphitiClient:
    """
    Manages Graphiti database connection and instance.
    Implements Singleton pattern to ensure single database connection.
    """
    
    _instance: Optional['GraphitiClient'] = None
    _graphiti: Optional[Graphiti] = None
    
    def __new__(cls) -> 'GraphitiClient':
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
    
    async def build_indices_and_constraints(self) -> None:
        """Build database indices and constraints."""
        await self.graphiti.build_indices_and_constraints()
        await self.graphiti.build_communities()
    
    async def verify_connection(self) -> None:
        """Verify database connectivity."""
        await self.graphiti.driver.client.verify_connectivity()
