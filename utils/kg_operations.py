"""
Knowledge Graph Operations
Handles all knowledge graph related operations including search, episode management, and data operations.
Follows Single Responsibility Principle - only manages KG operations.
"""

from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode
from graphiti_core.utils.maintenance.graph_data_operations import clear_data, retrieve_episodes
from database.graphiti_client import GraphitiClient

sample_markdown = """
# Software Requirements Specification (SRS)

Đây là phần giới thiệu tổng quan về tài liệu SRS.

## 1. Introduction

### 1.1 Purpose
Mục đích của tài liệu này là mô tả các yêu cầu cho hệ thống phần mềm.

### 1.2 Scope
Phạm vi của dự án bao gồm:
- Module A
- Module B
- Module C

## 2. System Requirements

### 2.1 Functional Requirements
Các yêu cầu chức năng bao gồm:

1. Người dùng có thể đăng nhập
2. Người dùng có thể xem thông tin
3. Người dùng có thể cập nhật dữ liệu

### 2.2 Non-Functional Requirements
Các yêu cầu phi chức năng:
- Performance: Response time < 2s
- Security: Mã hóa dữ liệu
- Availability: 99.9% uptime

## 3. System Architecture

### 3.1 Overview
Kiến trúc hệ thống sử dụng mô hình 3-tier.

### 3.2 Database Design
Thiết kế cơ sở dữ liệu bao gồm các bảng:
- Users
- Products
- Orders
"""

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
            update_communities=True
        )
    
    async def add_files_to_episodes(self, files: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        Add multiple files as episodes to the knowledge graph using bulk addition.
        
        Args:
            files: List of tuples containing (file_path, file_content)
            
        Returns:
            List of episode creation results
        """
        from utils.markdown_section_parser import MarkdownSectionParser
        parser = MarkdownSectionParser()
        
        # Collect all episodes for bulk addition
        bulk_episodes = []
        episode_metadata = []  # Track metadata for each episode
        
        for file_path, file_content in files:
            # Parse markdown
            sections = parser.parse_markdown_to_sections(file_content)

            for section in sections:
                # Create RawEpisode for bulk addition
                raw_episode = RawEpisode(
                    name=f"Document: {section['title']}",
                    content=section['raw_content'],
                    source=EpisodeType.text,
                    source_description=f"Heading from file: {section['title']}",
                    reference_time=datetime.now(timezone.utc)
                )
                
                bulk_episodes.append(raw_episode)
                episode_metadata.append({
                    "file_path": file_path,
                    "section_title": section['title']
                })
        
        # Add all episodes in bulk with fallback to individual additions
        if bulk_episodes:
            try:
                # Try bulk addition first
                bulk_result = await self.graphiti_client.graphiti.add_episode_bulk(bulk_episodes)
                
                # Format results to match expected return format
                results = []
                if bulk_result:
                    # Handle different possible return formats from bulk operation
                    if isinstance(bulk_result, list):
                        for i, episode_result in enumerate(bulk_result):
                            if episode_result and i < len(episode_metadata) and hasattr(episode_result, 'episode'):
                                episode_info = {
                                    "file_path": episode_metadata[i]["file_path"],
                                    "episode_uuid": episode_result.episode.uuid,
                                    "nodes_created": len(episode_result.nodes) if hasattr(episode_result, 'nodes') else 0,
                                    "edges_created": len(episode_result.edges) if hasattr(episode_result, 'edges') else 0
                                }
                                results.append(episode_info)
                    else:
                        # If bulk_result is not a list, it might be a single result or different format
                        # For now, we'll fall back to individual additions
                        raise ValueError("Unexpected bulk result format")
                
                return results
                
            except Exception as e:
                # If bulk addition fails, fall back to individual episode additions
                print(f"Bulk episode addition failed: {e}. Falling back to individual additions.")
                
                results = []
                for i, raw_episode in enumerate(bulk_episodes):
                    try:
                        result = await self.add_episode(
                            name=raw_episode.name,
                            content=raw_episode.content,
                            source_description=raw_episode.source_description
                        )
                        
                        if result and i < len(episode_metadata):
                            episode_info = {
                                "file_path": episode_metadata[i]["file_path"],
                                "episode_uuid": result.episode.uuid,
                                "nodes_created": len(result.nodes),
                                "edges_created": len(result.edges)
                            }
                            results.append(episode_info)
                    except Exception as individual_error:
                        print(f"Failed to add individual episode {raw_episode.name}: {individual_error}")
                        continue
                
                return results
        
        return []
    
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
