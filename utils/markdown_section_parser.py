import mistletoe
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from typing import List, Dict, Any
import re

class MarkdownSectionParser:
    """
    Class để parse markdown và chia thành các section theo heading
    """
    
    def __init__(self):
        self.sections = []
    
    def parse_markdown_to_sections(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Parse markdown content và chia thành các section theo heading
        
        Args:
            markdown_content (str): Nội dung markdown
            
        Returns:
            List[Dict]: Danh sách các section với structure:
            {
                'level': int,        # Cấp độ heading (1-6)
                'title': str,        # Tiêu đề heading
                'content': str,      # Nội dung markdown của section
                'raw_content': str   # Nội dung thô (không bao gồm heading)
            }
        """
        sections = []
        lines = markdown_content.split('\n')
        
        # Thu thập nội dung trước heading đầu tiên
        intro_content = []
        first_heading_index = -1
        
        # Tìm heading đầu tiên và thu thập nội dung intro
        for i, line in enumerate(lines):
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                first_heading_index = i
                break
            else:
                intro_content.append(line)
        
        # Chỉ tạo Introduction section nếu có nội dung có nghĩa
        intro_text = '\n'.join(intro_content).strip()
        if intro_text:
            intro_section = {
                'level': 0,
                'title': 'Introduction',
                'content': intro_text,
                'raw_content': intro_text
            }
            sections.append(intro_section)
        
        # Parse các heading sections
        current_section = None
        current_content = []
        
        start_index = first_heading_index if first_heading_index >= 0 else 0
        
        for i in range(start_index, len(lines)):
            line = lines[i]
            
            # Kiểm tra nếu là heading (bắt đầu bằng #)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if heading_match:
                # Lưu section trước đó nếu có
                if current_section is not None:
                    current_section['content'] = '\n'.join(current_content).strip()
                    current_section['raw_content'] = self._remove_heading_from_content(
                        current_section['content']
                    )
                    sections.append(current_section)
                
                # Tạo section mới
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                current_section = {
                    'level': level,
                    'title': title,
                    'content': '',
                    'raw_content': ''
                }
                current_content = [line]  # Bắt đầu với heading line
                
            else:
                # Thêm line vào section hiện tại
                if current_section is not None:
                    current_content.append(line)
        
        # Thêm section cuối cùng
        if current_section is not None:
            current_section['content'] = '\n'.join(current_content).strip()
            current_section['raw_content'] = self._remove_heading_from_content(
                current_section['content']
            )
            sections.append(current_section)
        
        return sections
    
    def _extract_heading_text(self, heading_token) -> str:
        """Trích xuất text từ heading token"""
        text_parts = []
        
        def extract_text_recursive(token):
            if hasattr(token, 'children') and token.children is not None:
                for child in token.children:
                    extract_text_recursive(child)
            elif hasattr(token, 'content'):
                text_parts.append(token.content)
        
        extract_text_recursive(heading_token)
        return ''.join(text_parts).strip()
    
    def _render_token_to_markdown(self, token) -> str:
        """Render một token thành markdown text"""
        try:
            # Tạo document tạm chứa token này
            temp_doc = Document('')
            temp_doc.children = [token]
            
            # Render thành markdown với error handling
            from mistletoe.markdown_renderer import MarkdownRenderer
            from mistletoe import block_token
            
            # Tạo renderer với safe initialization
            renderer = MarkdownRenderer()
            return renderer.render(temp_doc) + '\n'
            
        except (ValueError, AttributeError) as e:
            # Fallback: sử dụng AST renderer nếu MarkdownRenderer gặp lỗi
            try:
                from mistletoe.ast_renderer import ASTRenderer
                ast_renderer = ASTRenderer()
                ast_result = ast_renderer.render(temp_doc)
                
                # Convert AST back to simple markdown text
                return self._ast_to_markdown(ast_result) + '\n'
                
            except Exception as fallback_error:
                # Last resort: return raw content if available
                if hasattr(token, 'content'):
                    return str(token.content) + '\n'
                elif hasattr(token, 'children'):
                    return ''.join(str(child) for child in token.children) + '\n'
                else:
                    return str(token) + '\n'
    
    def _ast_to_markdown(self, ast_result) -> str:
        """Convert AST result back to simple markdown text"""
        if isinstance(ast_result, dict):
            if ast_result.get('type') == 'Document':
                children = ast_result.get('children', [])
                return ''.join(self._ast_to_markdown(child) for child in children)
            elif ast_result.get('type') == 'Paragraph':
                children = ast_result.get('children', [])
                return ''.join(self._ast_to_markdown(child) for child in children) + '\n\n'
            elif ast_result.get('type') == 'RawText':
                return ast_result.get('content', '')
            elif ast_result.get('type') == 'Heading':
                level = ast_result.get('level', 1)
                children = ast_result.get('children', [])
                heading_text = ''.join(self._ast_to_markdown(child) for child in children)
                return '#' * level + ' ' + heading_text + '\n\n'
            elif 'children' in ast_result:
                return ''.join(self._ast_to_markdown(child) for child in ast_result['children'])
            else:
                return ast_result.get('content', str(ast_result))
        elif isinstance(ast_result, list):
            return ''.join(self._ast_to_markdown(item) for item in ast_result)
        else:
            return str(ast_result)
    
    def _remove_heading_from_content(self, content: str) -> str:
        """Loại bỏ dòng heading đầu tiên khỏi content"""
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            return '\n'.join(lines[1:]).strip()
        return content.strip()
    
    def save_sections_to_files(self, sections: List[Dict], output_dir: str = "sections"):
        """
        Lưu các section thành các file riêng biệt
        
        Args:
            sections (List[Dict]): Danh sách sections
            output_dir (str): Thư mục lưu file
        """
        import os
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        for i, section in enumerate(sections):
            # Tạo tên file an toàn
            safe_title = re.sub(r'[^\w\s-]', '', section['title'])
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{i+1:02d}-{safe_title[:50]}.md"
            
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(section['content'])
            
            print(f"Đã lưu section '{section['title']}' vào {filepath}")
    
    def print_section_summary(self, sections: List[Dict]):
        """In tóm tắt các section"""
        print(f"\n=== TỔNG QUAN CÁC SECTION ===")
        print(f"Tổng số section: {len(sections)}")
        print("-" * 50)
        
        for i, section in enumerate(sections):
            # Tính số dòng chính xác, loại bỏ dòng trống cuối và đầu
            raw_content = section['raw_content'].strip()
            if raw_content:
                content_lines = len([line for line in raw_content.split('\n') if line.strip()])
            else:
                content_lines = 0
            content_chars = len(section['raw_content'])
            
            print(f"{i+1}. Level {section['level']}: {section['title']}")
            print(f"   - Số dòng: {content_lines}")
            print(f"   - Số ký tự: {content_chars}")
            print(f"   - Số ký tự: {raw_content}")
            print(f"   - Số ký tự: {section['content'].strip()}")
            print()