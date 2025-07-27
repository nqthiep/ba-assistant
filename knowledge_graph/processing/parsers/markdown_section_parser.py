"""
Markdown Section Parser
Layer 2 - Parse markdown content into structured sections using mistletoe.
"""

import mistletoe
from mistletoe import Document
from mistletoe.block_token import Heading, Paragraph, CodeFence, Quote, List as MistletoeList
from mistletoe.markdown_renderer import MarkdownRenderer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MarkdownSectionParser:
    """
    Parse markdown content into structured sections using mistletoe.
    Layer 2 - Handles markdown parsing as part of content processing pipeline.
    """
    
    def __init__(self):
        """Initialize the markdown parser with mistletoe renderer."""
        self._renderer = MarkdownRenderer()
    
    def parse_markdown_to_sections(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Parse markdown content into structured sections based on headings.
        
        Args:
            markdown_content (str): Raw markdown content
            
        Returns:
            List[Dict[str, Any]]: List of sections with structure:
            {
                'level': int,        # Heading level (1-6)
                'title': str,        # Heading title
                'content': str,      # Full markdown content including heading
                'raw_content': str   # Content without the heading line
            }
        """
        if not markdown_content or not markdown_content.strip():
            return []
        
        try:
            # Parse markdown using mistletoe
            doc = mistletoe.Document(markdown_content)
            sections = []
            
            # Collect content before first heading as introduction
            intro_tokens = []
            first_heading_found = False
            
            current_section = None
            current_tokens = []
            
            for token in doc.children:
                if isinstance(token, Heading):
                    # Save previous section if exists
                    if current_section is not None:
                        current_section['content'] = self._render_tokens_to_markdown(current_tokens)
                        current_section['raw_content'] = self._render_tokens_to_markdown(current_tokens[1:])  # Skip heading
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'level': token.level,
                        'title': self._extract_heading_text(token),
                        'content': '',
                        'raw_content': ''
                    }
                    current_tokens = [token]
                    first_heading_found = True
                    
                else:
                    if not first_heading_found:
                        # Collect intro content
                        intro_tokens.append(token)
                    else:
                        # Add to current section
                        if current_section is not None:
                            current_tokens.append(token)
            
            # Handle introduction section if exists
            if intro_tokens:
                intro_content = self._render_tokens_to_markdown(intro_tokens)
                if intro_content.strip():
                    intro_section = {
                        'level': 0,
                        'title': 'Introduction',
                        'content': intro_content,
                        'raw_content': intro_content
                    }
                    sections.insert(0, intro_section)
            
            # Add final section if exists
            if current_section is not None:
                current_section['content'] = self._render_tokens_to_markdown(current_tokens)
                current_section['raw_content'] = self._render_tokens_to_markdown(current_tokens[1:])  # Skip heading
                sections.append(current_section)
            
            logger.info(f"Successfully parsed markdown into {len(sections)} sections")
            return sections
            
        except Exception as e:
            logger.error(f"Failed to parse markdown content: {e}")
            # Fallback to simple regex-based parsing
            return self._fallback_regex_parsing(markdown_content)
    
    def _extract_heading_text(self, heading_token: Heading) -> str:
        """
        Extract text content from a heading token.
        
        Args:
            heading_token (Heading): Mistletoe heading token
            
        Returns:
            str: Clean heading text
        """
        try:
            # Create a temporary document with just the heading content
            temp_doc = Document('')
            temp_doc.children = heading_token.children
            
            # Render and clean up
            text = self._renderer.render(temp_doc).strip()
            return text
        except Exception as e:
            logger.warning(f"Failed to extract heading text, using fallback: {e}")
            # Fallback: try to get raw content
            if hasattr(heading_token, 'children') and heading_token.children:
                return str(heading_token.children[0]).strip()
            return "Untitled"
    
    def _render_tokens_to_markdown(self, tokens: List[Any]) -> str:
        """
        Render a list of mistletoe tokens back to markdown.
        
        Args:
            tokens (List[Any]): List of mistletoe tokens
            
        Returns:
            str: Rendered markdown content
        """
        if not tokens:
            return ""
        
        try:
            # Create temporary document with these tokens
            temp_doc = Document('')
            temp_doc.children = tokens
            
            # Render to markdown
            return self._renderer.render(temp_doc)
        except Exception as e:
            logger.warning(f"Failed to render tokens to markdown: {e}")
            # Fallback: convert tokens to string
            return '\n'.join(str(token) for token in tokens)
    
    def _fallback_regex_parsing(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Fallback regex-based parsing when mistletoe fails.
        
        Args:
            markdown_content (str): Raw markdown content
            
        Returns:
            List[Dict[str, Any]]: Parsed sections
        """
        import re
        
        logger.info("Using fallback regex parsing for markdown")
        sections = []
        lines = markdown_content.split('\n')
        
        # Collect intro content
        intro_content = []
        first_heading_index = -1
        
        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                first_heading_index = i
                break
            else:
                intro_content.append(line)
        
        # Add introduction section if exists
        intro_text = '\n'.join(intro_content).strip()
        if intro_text:
            sections.append({
                'level': 0,
                'title': 'Introduction',
                'content': intro_text,
                'raw_content': intro_text
            })
        
        # Parse heading sections
        current_section = None
        current_content = []
        
        start_index = first_heading_index if first_heading_index >= 0 else 0
        
        for i in range(start_index, len(lines)):
            line = lines[i]
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if heading_match:
                # Save previous section
                if current_section is not None:
                    current_section['content'] = '\n'.join(current_content).strip()
                    current_section['raw_content'] = '\n'.join(current_content[1:]).strip()  # Skip heading
                    sections.append(current_section)
                
                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                current_section = {
                    'level': level,
                    'title': title,
                    'content': '',
                    'raw_content': ''
                }
                current_content = [line]
            else:
                if current_section is not None:
                    current_content.append(line)
        
        # Add final section
        if current_section is not None:
            current_section['content'] = '\n'.join(current_content).strip()
            current_section['raw_content'] = '\n'.join(current_content[1:]).strip()  # Skip heading
            sections.append(current_section)
        
        return sections
    
    def get_section_summary(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics of parsed sections.
        
        Args:
            sections (List[Dict[str, Any]]): Parsed sections
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not sections:
            return {
                'total_sections': 0,
                'total_content_length': 0,
                'sections_by_level': {},
                'average_section_length': 0
            }
        
        total_content_length = sum(len(section.get('raw_content', '')) for section in sections)
        sections_by_level = {}
        
        for section in sections:
            level = section.get('level', 0)
            sections_by_level[level] = sections_by_level.get(level, 0) + 1
        
        return {
            'total_sections': len(sections),
            'total_content_length': total_content_length,
            'sections_by_level': sections_by_level,
            'average_section_length': total_content_length // len(sections) if sections else 0
        }
