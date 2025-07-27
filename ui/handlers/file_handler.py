"""
File Handler for Chainlit UI
Handles file upload, processing, and knowledge graph integration.
Follows Single Responsibility Principle - only manages file operations.
"""

import chainlit as cl
from typing import List, Tuple, Any
from .base_handler import BaseChainlitHandler
from .response_formatter import ResponseFormatter
from ..constants import FileTypes, FileSettings, UIMessages


class FileHandler(BaseChainlitHandler):
    """
    Handles file upload and processing operations.
    
    Responsibilities:
    - File upload request and management
    - File processing pipeline coordination
    - Integration with knowledge graph services
    - File operation result formatting
    
    Follows SOLID principles:
    - Single Responsibility: Only handles file operations
    - Open/Closed: Easy to extend with new file types or processing methods
    - Dependency Inversion: Uses BA Knowledge Service abstraction
    """
    
    def __init__(self, factory):
        """
        Initialize file handler.
        
        Args:
            factory: KnowledgeGraphFactory for dependency injection
        """
        super().__init__(factory)
        self.supported_file_types = FileTypes.get_supported_types()
    
    async def handle(self, files: List[Any]) -> None:
        """
        Main handler method for file processing.
        
        Args:
            files: List of uploaded files to process
        """
        await self.process_uploaded_files(files)
    
    async def ask_file_source(self) -> None:
        """
        Ask user to upload files for knowledge graph building.
        Displays file upload dialog with supported file types.
        """
        files = await cl.AskFileMessage(
            max_size_mb=FileSettings.MAX_SIZE_MB,
            max_files=FileSettings.MAX_FILES,
            content=UIMessages.FILE_UPLOAD_REQUEST,
            accept=self.supported_file_types
        ).send()
        
        if files:
            await self.process_uploaded_files(files)
    
    async def process_uploaded_files(self, files: List[Any]) -> None:
        """
        Process uploaded files using the new Layer 2 pipeline.
        
        Args:
            files: List of uploaded files to process
        """
        # Extract file names for user notification
        file_names = [self._get_file_name(file) for file in files]
        
        # Notify user that processing has started
        start_message = ResponseFormatter.format_file_processing_start(file_names)
        await self.send_message(start_message)
        
        # Process files using BA knowledge service (Layer 3)
        result = await self.ba_knowledge.process_uploaded_files(files)
        
        # Send formatted results to user
        await self._send_processing_result(result)
    
    async def add_files_to_episodes(self, files: List[Tuple[str, str]]) -> None:
        """
        Add uploaded files to knowledge graph episodes.
        Legacy method for backward compatibility.
        
        Args:
            files: List of tuples containing (file_path, file_content)
        """
        # Extract file paths for user notification
        file_names = [file_path for file_path, _ in files]
        
        # Notify user that processing has started
        start_message = ResponseFormatter.format_file_processing_start(file_names)
        await self.send_message(start_message)
        
        # Add files to knowledge graph using Layer 3
        result = await self.ba_knowledge.add_business_documents(files)
        
        # Send formatted results to user
        await self._send_processing_result(result)
    
    async def _send_processing_result(self, result: dict) -> None:
        """
        Send formatted processing result to user.
        
        Args:
            result: Processing result dictionary from BA knowledge service
        """
        if result.get("status") == "success":
            success_message = ResponseFormatter.format_processing_success(result)
            await self.send_message(success_message)
        else:
            error_message = ResponseFormatter.format_processing_error(result)
            await self.send_message(error_message)
    
    def _get_file_name(self, file: Any) -> str:
        """
        Extract file name from file object.
        
        Args:
            file: File object with name or path attribute
            
        Returns:
            File name string
        """
        if hasattr(file, 'name'):
            return file.name
        elif hasattr(file, 'path'):
            return file.path
        else:
            return "Unknown file"
    
    def get_supported_file_types(self) -> List[str]:
        """
        Get list of supported file MIME types.
        
        Returns:
            List of supported MIME type strings
        """
        return self.supported_file_types.copy()
    
    def add_supported_file_type(self, mime_type: str) -> None:
        """
        Add new supported file type.
        Useful for extending file support without modifying existing code.
        
        Args:
            mime_type: MIME type string to add
        """
        if mime_type not in self.supported_file_types:
            self.supported_file_types.append(mime_type)
    
    def remove_supported_file_type(self, mime_type: str) -> None:
        """
        Remove supported file type.
        
        Args:
            mime_type: MIME type string to remove
        """
        if mime_type in self.supported_file_types:
            self.supported_file_types.remove(mime_type)
    
    async def validate_files(self, files: List[Any]) -> Tuple[List[Any], List[str]]:
        """
        Validate uploaded files against supported types and size limits.
        Future method for enhanced file validation.
        
        Args:
            files: List of files to validate
            
        Returns:
            Tuple of (valid_files, error_messages)
        """
        # Future implementation for file validation
        # Would include checks for:
        # - File type validation
        # - File size limits
        # - File content validation
        # - Security checks
        
        return files, []
    
    async def process_files_in_batches(self, files: List[Any], batch_size: int = 5) -> None:
        """
        Process files in batches for better performance.
        Future method for handling large file uploads.
        
        Args:
            files: List of files to process
            batch_size: Number of files to process per batch
        """
        # Future implementation for batch processing
        # Useful for handling large numbers of files efficiently
        pass
