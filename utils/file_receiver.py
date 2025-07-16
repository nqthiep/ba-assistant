from typing import List

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

# llm_transformer = LLMGraphTransformer(llm=llm)

# Ensure you import cl, MarkItDown, Document, llm_transformer from their correct modules
# If these are not globally available, update the import paths accordingly

async def on_file_receiver(files: List):
    """
    Handle file reception: notify user, convert files to markdown, and build knowledge graph documents.
    Args:
        files (list): List of uploaded file objects.
    """
    # Import cl and MarkItDown locally to avoid circular import
    import chainlit as cl
    from markitdown import MarkItDown

    md = MarkItDown(enable_plugins=True)  # Set to True to enable plugins
    return [(file.path, md.convert(file.path).text_content) for file in files]
