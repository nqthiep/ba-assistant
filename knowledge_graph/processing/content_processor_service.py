"""
Content Processor Service
Layer 2 - Concrete implementation of common content processing operations.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Union
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

from .content_processor_interface import ContentProcessorInterface
from knowledge_graph.core.graphiti_core_interface import GraphitiCoreInterface
from knowledge_graph.core.graphiti_core_service import GraphitiCoreService


class ContentProcessorService(ContentProcessorInterface):
    """
    Concrete implementation of content processing operations.
    Layer 2 - Uses Layer 1 (Core) for actual Graphiti interactions.
    """
    
    def __init__(self, core_service: GraphitiCoreInterface = None):
        self._core = core_service or GraphitiCoreService()
    
    async def add_text_content(
        self, 
        text: str, 
        title: str, 
        source_description: str = "Text content"
    ) -> Dict[str, Any]:
        """Add text content as an episode to the knowledge graph."""
        result = await self._core.add_single_episode(
            name=title,
            content=text,
            source=EpisodeType.text,
            source_description=source_description,
            reference_time=datetime.now(timezone.utc)
        )
        
        episode_info = {
            "title": title,
            "episode_uuid": result.episode.uuid if result and hasattr(result, 'episode') else None,
            "nodes_created": len(result.nodes) if result and hasattr(result, 'nodes') else 0,
            "edges_created": len(result.edges) if result and hasattr(result, 'edges') else 0,
            "content_length": len(text)
        }
        
        return {
            "success": True,
            "message": f"Successfully processed 1 episode: {title}",
            "episodes_added": 1,
            "content_processed": title,
            "details": [episode_info]
        }
    
    async def add_file_content(
        self, 
        file_path: str, 
        file_content: str
    ) -> Dict[str, Any]:
        """Add file content as episodes to the knowledge graph using bulk processing."""
        from utils.markdown_section_parser import MarkdownSectionParser
        parser = MarkdownSectionParser()
        
        # Parse markdown into sections
        sections = parser.parse_markdown_to_sections(file_content)
        
        # Collect all episodes for bulk addition
        bulk_episodes = []
        episode_metadata = []
        
        for section in sections:
            raw_episode = RawEpisode(
                name=f"Document: {section['title']}",
                content=section['raw_content'],
                source=EpisodeType.text,
                source_description=f"Section from file: {file_path}",
                reference_time=datetime.now(timezone.utc)
            )
            
            bulk_episodes.append(raw_episode)
            episode_metadata.append({
                "file_path": file_path,
                "section_title": section['title'],
                "content_length": len(section['raw_content'])
            })
        
        # Use bulk addition - Layer 1 (Core) handles fallback logic
        bulk_result = await self._core.add_bulk_episodes(bulk_episodes)
           
        results = []
        if bulk_result and isinstance(bulk_result, list):
            # Process results from Layer 1 (handles both bulk and individual fallback)
            for i, episode in enumerate(bulk_result):
                if episode and i < len(episode_metadata):
                    # Episode object should have uuid directly, or through .episode
                    episode_uuid = None
                    if hasattr(episode, 'uuid'):
                        episode_uuid = episode.uuid
                    elif hasattr(episode, 'episode') and hasattr(episode.episode, 'uuid'):
                        episode_uuid = episode.episode.uuid
                    
                    if episode_uuid:
                        episode_info = {
                            **episode_metadata[i],
                            "episode_uuid": episode_uuid,
                            "nodes_created": len(episode.nodes) if hasattr(episode, 'nodes') else 1,
                            "edges_created": len(episode.edges) if hasattr(episode, 'edges') else 0
                        }
                        results.append(episode_info)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(results)} episodes from file: {file_path}",
            "episodes_added": len(results),
            "file_processed": file_path,
            "details": results
        }
    
    async def add_multiple_files(
        self, 
        files: List[Tuple[str, str]]
    ) -> List[Dict[str, Any]]:
        """Add multiple files as episodes using bulk processing."""
        from utils.markdown_section_parser import MarkdownSectionParser
        parser = MarkdownSectionParser()
        
        # Collect all episodes for bulk addition
        bulk_episodes = []
        episode_metadata = []
        
        for file_path, file_content in files:
            sections = parser.parse_markdown_to_sections(file_content)
            
            for section in sections:
                raw_episode = RawEpisode(
                    name=f"Document: {section['title']}",
                    content=section['raw_content'],
                    source=EpisodeType.text,
                    source_description=f"Section from file: {file_path}",
                    reference_time=datetime.now(timezone.utc)
                )
                
                bulk_episodes.append(raw_episode)
                episode_metadata.append({
                    "file_path": file_path,
                    "section_title": section['title'],
                    "content_length": len(section['raw_content'])
                })
        
        # Use bulk addition - Layer 1 (Core) handles fallback logic
        bulk_result = await self._core.add_bulk_episodes(bulk_episodes)
        
        results = []
        if bulk_result and isinstance(bulk_result, list):
            # Process results from Layer 1 (handles both bulk and individual fallback)
            for i, episode in enumerate(bulk_result):
                if episode and i < len(episode_metadata):
                    # Episode object should have uuid directly, or through .episode
                    episode_uuid = None
                    if hasattr(episode, 'uuid'):
                        episode_uuid = episode.uuid
                    elif hasattr(episode, 'episode') and hasattr(episode.episode, 'uuid'):
                        episode_uuid = episode.episode.uuid
                    
                    if episode_uuid:
                        episode_info = {
                            **episode_metadata[i],
                            "episode_uuid": episode_uuid,
                            "nodes_created": len(episode.nodes) if hasattr(episode, 'nodes') else 1,
                            "edges_created": len(episode.edges) if hasattr(episode, 'edges') else 0
                        }
                        results.append(episode_info)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(results)} episodes from {len(files)} files",
            "episodes_added": len(results),
            "files_processed": len(files),
            "details": results
        }
    
    async def add_json_content(
        self, 
        json_data: Dict[str, Any], 
        title: str,
        source_description: str = "JSON data"
    ) -> Dict[str, Any]:
        """Add JSON data as an episode to the knowledge graph."""
        content = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        result = await self._core.add_single_episode(
            name=title,
            content=content,
            source=EpisodeType.text,
            source_description=source_description,
            reference_time=datetime.now(timezone.utc)
        )
        
        episode_info = {
            "title": title,
            "episode_uuid": result.episode.uuid if result and hasattr(result, 'episode') else None,
            "nodes_created": len(result.nodes) if result and hasattr(result, 'nodes') else 0,
            "edges_created": len(result.edges) if result and hasattr(result, 'edges') else 0,
            "content_length": len(content),
            "json_keys": list(json_data.keys()) if isinstance(json_data, dict) else []
        }
        
        return {
            "success": True,
            "message": f"Successfully processed 1 episode: {title}",
            "episodes_added": 1,
            "content_processed": title,
            "details": [episode_info]
        }
    
    async def add_structured_content(
        self, 
        content_items: List[Dict[str, Union[str, Dict]]]
    ) -> Dict[str, Any]:
        """Add structured content items to the knowledge graph using bulk processing."""
        # Collect all episodes for bulk addition
        bulk_episodes = []
        episode_metadata = []
        
        for item in content_items:
            title = item.get('title', 'Untitled')
            content = item.get('content', '')
            metadata = item.get('metadata', {})
            
            # Convert content to string if it's not already
            if isinstance(content, dict):
                content = json.dumps(content, indent=2, ensure_ascii=False)
            elif not isinstance(content, str):
                content = str(content)
            
            source_description = metadata.get('source_description', 'Structured content')
            
            raw_episode = RawEpisode(
                name=title,
                content=content,
                source=EpisodeType.text,
                source_description=source_description,
                reference_time=datetime.now(timezone.utc)
            )
            
            bulk_episodes.append(raw_episode)
            episode_metadata.append({
                "title": title,
                "content_length": len(content),
                "metadata": metadata
            })
        
        # Use bulk addition - Layer 1 (Core) handles fallback logic
        bulk_result = await self._core.add_bulk_episodes(bulk_episodes)
        
        results = []
        if bulk_result and isinstance(bulk_result, list):
            # Process results from Layer 1 (handles both bulk and individual fallback)
            for i, episode in enumerate(bulk_result):
                if episode and i < len(episode_metadata):
                    # Episode object should have uuid directly, or through .episode
                    episode_uuid = None
                    if hasattr(episode, 'uuid'):
                        episode_uuid = episode.uuid
                    elif hasattr(episode, 'episode') and hasattr(episode.episode, 'uuid'):
                        episode_uuid = episode.episode.uuid
                    
                    if episode_uuid:
                        episode_info = {
                            **episode_metadata[i],
                            "episode_uuid": episode_uuid,
                            "nodes_created": len(episode.nodes) if hasattr(episode, 'nodes') else 1,
                            "edges_created": len(episode.edges) if hasattr(episode, 'edges') else 0
                        }
                        results.append(episode_info)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(results)} episodes from {len(content_items)} structured content items",
            "episodes_added": len(results),
            "content_processed": f"{len(content_items)} structured items",
            "details": results
        }
    
    async def search_content(self, query: str) -> List[Any]:
        """Search for content in the knowledge graph."""
        return await self._core.search_graph(query)
    
    async def clear_all_content(self) -> None:
        """Clear all content from the knowledge graph."""
        await self._core.clear_all_data()
