"""
Document Converter
Layer 2 - Convert various file formats to markdown content.
"""

from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class DocumentConverter:
    """
    Convert various file formats to markdown content using MarkItDown.
    Layer 2 - Handles file format conversion as part of content processing pipeline.
    """
    
    def __init__(self):
        """Initialize the document converter with MarkItDown."""
        try:
            from markitdown import MarkItDown
            self._markitdown = MarkItDown(enable_plugins=True)
        except ImportError as e:
            logger.error(f"Failed to import MarkItDown: {e}")
            raise ImportError("MarkItDown is required for document conversion. Please install it.")
    
    def convert_file_to_markdown(self, file_path: str) -> str:
        """
        Convert a single file to markdown content.
        
        Args:
            file_path (str): Path to the file to convert
            
        Returns:
            str: Markdown content of the file
            
        Raises:
            Exception: If file conversion fails
        """
        try:
            result = self._markitdown.convert(file_path)
            return result.text_content if result else ""
        except Exception as e:
            logger.error(f"Failed to convert file {file_path}: {e}")
            raise Exception(f"Document conversion failed for {file_path}: {str(e)}")
    
    def convert_files_to_markdown(self, files: List[Any]) -> List[Tuple[str, str]]:
        """
        Convert multiple files to markdown content.
        
        Args:
            files (List[Any]): List of file objects with .path attribute
            
        Returns:
            List[Tuple[str, str]]: List of (file_path, markdown_content) tuples
            
        Raises:
            Exception: If any file conversion fails
        """
        converted_files = []
        failed_files = []
        
        for file in files:
            try:
                file_path = file.path
                markdown_content = self.convert_file_to_markdown(file_path)
                converted_files.append((file_path, markdown_content))
                logger.info(f"Successfully converted file: {file_path}")
            except Exception as e:
                failed_files.append((file.path if hasattr(file, 'path') else str(file), str(e)))
                logger.error(f"Failed to convert file: {e}")
        
        if failed_files:
            failed_list = [f"- {path}: {error}" for path, error in failed_files]
            error_message = f"Failed to convert {len(failed_files)} files:\n" + "\n".join(failed_list)
            
            if not converted_files:
                # All files failed
                raise Exception(f"All file conversions failed:\n{error_message}")
            else:
                # Some files failed, log warning but continue
                logger.warning(f"Some files failed conversion: {error_message}")
        
        return converted_files
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List[str]: List of supported MIME types
        """
        return [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            "text/markdown",             # .md
            "text/html",                 # .html
            "application/pdf",           # .pdf
            "text/plain"                 # .txt
        ]
    
    def is_supported_format(self, mime_type: str) -> bool:
        """
        Check if a file format is supported.
        
        Args:
            mime_type (str): MIME type to check
            
        Returns:
            bool: True if format is supported
        """
        return mime_type in self.get_supported_formats()
