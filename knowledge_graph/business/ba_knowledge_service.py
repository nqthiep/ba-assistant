"""
BA Knowledge Service
Layer 3 - Concrete implementation of project-specific BA Assistant knowledge operations.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
import os

from .ba_knowledge_interface import BAKnowledgeInterface
from knowledge_graph.processing import ContentProcessorInterface, ContentProcessorService
from knowledge_graph.core.graphiti_core_interface import GraphitiCoreInterface
from knowledge_graph.core.graphiti_core_service import GraphitiCoreService


class BAKnowledgeService(BAKnowledgeInterface):
    """
    Concrete implementation of BA Assistant knowledge operations.
    Layer 3 - Uses Layer 2 (Processing) for content processing and implements business logic specific to BA Assistant.
    """
    
    def __init__(
        self, 
        content_processor: ContentProcessorInterface = None,
        core_service: GraphitiCoreInterface = None
    ):
        self._content_processor = content_processor or ContentProcessorService()
        self._core = core_service or GraphitiCoreService()
    
    async def search_business_knowledge(self, query: str) -> str:
        """Search business knowledge and format results for BA Assistant UI."""
        try:
            edges = await self._content_processor.search_content(query)
            return self._format_search_results(edges)
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    async def process_uploaded_files(
        self, 
        files: List[Any]
    ) -> Dict[str, Any]:
        """
        Process uploaded files through the complete document processing pipeline.
        
        This method uses the new Layer 2 pipeline that:
        1. Converts files to markdown
        2. Parses markdown into sections
        3. Adds sections as episodes to knowledge graph
        
        Args:
            files (List[Any]): List of uploaded file objects
            
        Returns:
            Dict[str, Any]: Business-formatted response with categorized results
        """
        try:
            # Use the new complete pipeline from Layer 2
            result = await self._content_processor.process_uploaded_files(files)
            
            if not result.get("success", False):
                return {
                    "status": "error",
                    "message": result.get("message", "Unknown error occurred"),
                    "summary": {
                        "total_files": len(files),
                        "total_episodes": 0,
                        "total_nodes": 0,
                        "total_edges": 0
                    },
                    "by_category": {
                        "requirements": [],
                        "design_docs": [],
                        "user_manuals": [],
                        "other": []
                    },
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "error": result.get("error")
                }
            
            # Extract details from Layer 2 response
            episode_details = result.get("details", [])
            
            # Categorize results by document type (business logic)
            categorized_results = {
                "requirements": [],
                "design_docs": [],
                "user_manuals": [],
                "other": []
            }
            
            total_episodes = result.get("episodes_added", 0)
            total_nodes = 0
            total_edges = 0
            
            for episode_detail in episode_details:
                file_path = episode_detail.get("file_path", "")
                total_nodes += episode_detail.get("nodes_created", 0)
                total_edges += episode_detail.get("edges_created", 0)
                
                # Business logic: Categorize by file path
                if "requirements" in file_path.lower() or "requirement" in file_path.lower():
                    categorized_results["requirements"].append(episode_detail)
                elif "design" in file_path.lower() or "architecture" in file_path.lower():
                    categorized_results["design_docs"].append(episode_detail)
                elif "manual" in file_path.lower() or "user" in file_path.lower() or "guide" in file_path.lower():
                    categorized_results["user_manuals"].append(episode_detail)
                else:
                    categorized_results["other"].append(episode_detail)
            
            return {
                "status": "success",
                "message": result.get("message", "Files processed successfully"),
                "summary": {
                    "total_files": result.get("files_processed", len(files)),
                    "total_episodes": total_episodes,
                    "total_nodes": total_nodes,
                    "total_edges": total_edges
                },
                "by_category": categorized_results,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process uploaded files: {str(e)}",
                "summary": {
                    "total_files": len(files),
                    "total_episodes": 0,
                    "total_nodes": 0,
                    "total_edges": 0
                },
                "by_category": {
                    "requirements": [],
                    "design_docs": [],
                    "user_manuals": [],
                    "other": []
                },
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    async def add_business_documents(
        self, 
        documents: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """Add business documents to the knowledge graph."""
        try:
            result = await self._content_processor.add_multiple_files(documents)
            
            # Extract details from new structured format
            episode_details = result.get("details", [])
            
            # Categorize results by document type
            categorized_results = {
                "requirements": [],
                "design_docs": [],
                "user_manuals": [],
                "other": []
            }
            
            total_episodes = result.get("episodes_added", 0)
            total_nodes = 0
            total_edges = 0
            
            for episode_detail in episode_details:
                file_path = episode_detail.get("file_path", "")
                total_nodes += episode_detail.get("nodes_created", 0)
                total_edges += episode_detail.get("edges_created", 0)
                
                # Categorize by file path
                if "requirements" in file_path.lower():
                    categorized_results["requirements"].append(episode_detail)
                elif "design" in file_path.lower():
                    categorized_results["design_docs"].append(episode_detail)
                elif "manual" in file_path.lower() or "user" in file_path.lower():
                    categorized_results["user_manuals"].append(episode_detail)
                else:
                    categorized_results["other"].append(episode_detail)
            
            return {
                "status": "success",
                "summary": {
                    "total_documents": len(documents),
                    "total_episodes": total_episodes,
                    "total_nodes": total_nodes,
                    "total_edges": total_edges
                },
                "by_category": categorized_results,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add business documents: {str(e)}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def add_requirement_document(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """Add a business requirement document to the knowledge graph."""
        try:
            result = await self._content_processor.add_file_content(file_path, content)
            
            # Extract details from new structured format
            episode_details = result.get("details", [])
            
            return {
                "status": "success",
                "document_type": "requirement",
                "file_path": file_path,
                "sections_processed": result.get("episodes_added", 0),
                "total_nodes": sum(r.get("nodes_created", 0) for r in episode_details),
                "total_edges": sum(r.get("edges_created", 0) for r in episode_details),
                "sections": [r.get("section_title") for r in episode_details],
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "document_type": "requirement",
                "file_path": file_path,
                "message": f"Failed to add requirement document: {str(e)}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def add_design_document(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """Add a design document to the knowledge graph."""
        try:
            result = await self._content_processor.add_file_content(file_path, content)
            
            # Extract details from new structured format
            episode_details = result.get("details", [])
            
            return {
                "status": "success",
                "document_type": "design",
                "file_path": file_path,
                "sections_processed": result.get("episodes_added", 0),
                "total_nodes": sum(r.get("nodes_created", 0) for r in episode_details),
                "total_edges": sum(r.get("edges_created", 0) for r in episode_details),
                "sections": [r.get("section_title") for r in episode_details],
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "document_type": "design",
                "file_path": file_path,
                "message": f"Failed to add design document: {str(e)}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def add_user_manual(
        self, 
        file_path: str, 
        content: str
    ) -> Dict[str, Any]:
        """Add a user manual to the knowledge graph."""
        try:
            result = await self._content_processor.add_file_content(file_path, content)
            
            # Extract details from new structured format
            episode_details = result.get("details", [])
            
            return {
                "status": "success",
                "document_type": "user_manual",
                "file_path": file_path,
                "sections_processed": result.get("episodes_added", 0),
                "total_nodes": sum(r.get("nodes_created", 0) for r in episode_details),
                "total_edges": sum(r.get("edges_created", 0) for r in episode_details),
                "sections": [r.get("section_title") for r in episode_details],
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "document_type": "user_manual",
                "file_path": file_path,
                "message": f"Failed to add user manual: {str(e)}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """Get the status of the BA Assistant knowledge graph."""
        try:
            # Check basic initialization
            if not self._core.is_initialized():
                return {
                    "status": "error", 
                    "message": "Knowledge system not initialized",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Check database connection
            try:
                await self._core.verify_connection()
            except Exception as e:
                return {
                    "status": "error", 
                    "message": f"Database connection failed: {e}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Check for existing data
            try:
                episodes = await self._core.retrieve_episodes(
                    reference_time=datetime.now(timezone.utc),
                    last_n=10
                )
                
                return {
                    "status": "ready",
                    "message": "BA Assistant knowledge system is operational",
                    "has_data": len(episodes) > 0,
                    "recent_episodes_count": len(episodes),
                    "system_type": "BA Assistant Knowledge Graph",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    "status": "warning", 
                    "message": f"System ready but data check failed: {e}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Status check failed: {e}",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def clear_business_knowledge(self) -> Dict[str, Any]:
        """Clear all business knowledge from the graph."""
        try:
            await self._content_processor.clear_all_content()
            return {
                "status": "success",
                "message": "All business knowledge has been cleared",
                "cleared_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to clear business knowledge: {str(e)}",
                "attempted_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def initialize_knowledge_system(self) -> Dict[str, Any]:
        """Initialize the knowledge system for BA Assistant."""
        try:
            await self._core.build_indices_and_constraints()
            return {
                "status": "success",
                "message": "BA Assistant knowledge system initialized successfully",
                "system_type": "BA Assistant Knowledge Graph",
                "initialized_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize knowledge system: {str(e)}",
                "attempted_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_document_summary(self) -> Dict[str, Any]:
        """Get a summary of all documents in the knowledge graph."""
        try:
            # Retrieve recent episodes to analyze document distribution
            episodes = await self._core.retrieve_episodes(
                reference_time=datetime.now(timezone.utc),
                last_n=100
            )
            
            # Analyze episode sources to categorize documents
            document_types = {
                "requirements": 0,
                "design_docs": 0,
                "user_manuals": 0,
                "other": 0
            }
            
            for episode in episodes:
                source_desc = getattr(episode, 'source_description', '').lower()
                if 'requirement' in source_desc:
                    document_types["requirements"] += 1
                elif 'design' in source_desc:
                    document_types["design_docs"] += 1
                elif 'manual' in source_desc or 'user' in source_desc:
                    document_types["user_manuals"] += 1
                else:
                    document_types["other"] += 1
            
            return {
                "status": "success",
                "total_episodes": len(episodes),
                "document_distribution": document_types,
                "summary_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate document summary: {str(e)}",
                "attempted_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def search_by_document_type(
        self, 
        document_type: str, 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """Search for content by document type."""
        try:
            # Create a search query that includes document type
            search_query = f"{document_type} {query}".strip()
            edges = await self._content_processor.search_content(search_query)
            
            # Filter and format results
            results = []
            for edge in edges:
                result = {
                    "content": getattr(edge, 'fact', str(edge)),
                    "document_type": document_type,
                    "relevance_score": getattr(edge, 'score', 0),
                    "source": getattr(edge, 'source', 'unknown')
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            return [{
                "error": f"Search failed: {str(e)}",
                "document_type": document_type,
                "query": query
            }]
    
    def _format_search_results(self, edges: List[Any]) -> str:
        """Format search results for BA Assistant UI display."""
        if not edges:
            return "No business knowledge found for your query."
        
        formatted_results = []
        for i, edge in enumerate(edges[:10], 1):  # Limit to top 10 results
            fact = getattr(edge, 'fact', str(edge))
            formatted_results.append(f"{i}. {fact}")
        
        result_text = "\n\n".join(formatted_results)
        
        if len(edges) > 10:
            result_text += f"\n\n... and {len(edges) - 10} more results."
        
        return result_text
