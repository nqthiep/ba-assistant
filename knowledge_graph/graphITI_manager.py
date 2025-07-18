import os
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig  
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig  
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

class GraphITIManager:
    def __init__(self, neo4j_url="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="Kim@cuong2"):
        """Initialize GraphITI manager with Neo4j and Google API configurations."""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        self.graphiti = Graphiti(
            neo4j_url,
            neo4j_user,
            neo4j_password,
            llm_client=GeminiClient(
                config=LLMConfig(
                    api_key=self.api_key,
                    model="gemini-2.0-flash"
                )
            ),
            embedder=GeminiEmbedder(
                config=GeminiEmbedderConfig(
                    api_key=self.api_key,
                    embedding_model="embedding-001"
                )
            ),
            cross_encoder=GeminiRerankerClient(
                config=LLMConfig(
                    api_key=self.api_key,
                    model="gemini-2.5-flash-lite-preview-06-17"
                )
            )
        )

    async def add_episode_to_graph(self, filename: str, document_content: str, group_id: str, 
                                 source_description: str = 'Description of source') -> dict:
        """
        Add an episode to the Graphiti knowledge graph.
        
        Args:
            filename (str): Name of the file being processed
            document_content (str): Content of the document to add
            group_id (str): Group ID for versioning
            source_description (str, optional): Description of the source
            
        Returns:
            dict: Response from Graphiti API
        """
        try:
            response = await self.graphiti.add_episode(
                name=filename,
                episode_body=document_content,
                group_id=group_id,
                reference_time=datetime.now().isoformat(),
                source_description=source_description
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to add episode to graph: {str(e)}")

    async def get_graph(self, group_id: str) -> dict:
        """
        Retrieve a graph by group ID.
        
        Args:
            group_id (str): The group ID to look up
            
        Returns:
            dict: Graph data if found
        """
        try:
            return await self.graphiti.get_graph(group_id=group_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve graph: {str(e)}")