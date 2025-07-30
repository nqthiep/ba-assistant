import os
from pathlib import Path
from typing import Dict, Optional

class PromptLoader:
    """Utility class for loading prompt templates from Markdown files."""
    
    def __init__(self):
        self.prompt_dir = Path(__file__).parent.parent / "agents" / "prompts"
        self.cache: Dict[str, str] = {}
        
    def load_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Load a prompt template from a Markdown file.
        
        Args:
            prompt_name (str): Name of the prompt file (without .md extension)
            
        Returns:
            Optional[str]: The prompt content if found, None otherwise
        """
        try:
            # Check cache first
            if prompt_name in self.cache:
                return self.cache[prompt_name]
            
            # Construct file path
            file_path = self.prompt_dir / f"{prompt_name}.md"
            
            # Check if file exists
            if not file_path.exists():
                print(f"Warning: Prompt file not found: {file_path}")
                return None
            
            # Read content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Cache the content
            self.cache[prompt_name] = content
            return content
            
        except Exception as e:
            print(f"Error loading prompt {prompt_name}: {str(e)}")
            return None
    
    def refresh_cache(self) -> None:
        """Clear the prompt cache to reload from files."""
        self.cache.clear()
    
    def list_available_prompts(self) -> list[str]:
        """List all available prompt templates."""
        try:
            return [f.stem for f in self.prompt_dir.glob("*.md")]
        except Exception as e:
            print(f"Error listing prompts: {str(e)}")
            return []

# Create singleton instance
prompt_loader = PromptLoader()