"""
Utility functions for the RAG tools.
"""

import logging
import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    LOCATION,
    PROJECT_ID,
    DEFAULT_CORPUS_ID,
    DEFAULT_CORPUS_DISPLAY_NAME,
)

logger = logging.getLogger(__name__)


def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convert a corpus name to its full resource name if needed.
    Handles various input formats and ensures the returned name follows Vertex AI's requirements.

    Args:
        corpus_name (str): The corpus name or display name

    Returns:
        str: The full resource name of the corpus
    """
    logger.info(f"Getting resource name for corpus: {corpus_name}")

    # If it's already a full resource name with the projects/locations/ragCorpora format
    if re.match(r"^projects/[^/]+/locations/[^/]+/ragCorpora/[^/]+$", corpus_name):
        return corpus_name

    # Check if this matches the default corpus display name
    if corpus_name == DEFAULT_CORPUS_DISPLAY_NAME:
        return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{DEFAULT_CORPUS_ID}"

    # Check if this is a display name of an existing corpus
    try:
        # List all corpora and check if there's a match with the display name
        corpora = rag.list_corpora()
        for corpus in corpora:
            if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
                return corpus.name
    except Exception as e:
        logger.warning(f"Error when checking for corpus display name: {str(e)}")
        # If we can't check and it's a simple name, try the default corpus
        if corpus_name.lower() in ["test", "default"] or not re.search(r"[^a-zA-Z0-9_-]", corpus_name):
            logger.info(f"Defaulting to configured corpus for: {corpus_name}")
            return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{DEFAULT_CORPUS_ID}"

    # If it contains partial path elements, extract just the corpus ID
    if "/" in corpus_name:
        # Extract the last part of the path as the corpus ID
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name

    # Remove any special characters that might cause issues
    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    # Construct the standardized resource name
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Check if a corpus with the given name exists.

    Args:
        corpus_name (str): The name of the corpus to check
        tool_context (ToolContext): The tool context for state management

    Returns:
        bool: True if the corpus exists, False otherwise
    """
    # Check state first if tool_context is provided
    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True

    try:
        # Get full resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # List all corpora and check if this one exists
        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):
                # Update state
                tool_context.state[f"corpus_exists_{corpus_name}"] = True
                # Also set this as the current corpus if no current corpus is set
                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking if corpus exists: {str(e)}")
        # If we can't check, assume it doesn't exist
        return False


def set_current_corpus(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Set the current corpus in the tool context state.

    Args:
        corpus_name (str): The name of the corpus to set as current
        tool_context (ToolContext): The tool context for state management

    Returns:
        bool: True if the corpus exists and was set as current, False otherwise
    """
    # Check if corpus exists first
    if check_corpus_exists(corpus_name, tool_context):
        tool_context.state["current_corpus"] = corpus_name
        return True
    return False


if __name__ == "__main__":
    # When running as a script, handle imports differently
    import sys
    import os
    
    # Add the parent directory to the path so we can import from rag_agent
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Import config directly
    from rag_agent.config import PROJECT_ID, LOCATION, DEFAULT_CORPUS_ID, DEFAULT_CORPUS_DISPLAY_NAME
    
    # Test the function
    test_corpus_name = "test"
    result = get_corpus_resource_name(test_corpus_name)
    print(f"Input: '{test_corpus_name}'")
    print(f"Output: '{result}'")
    
    # Test with different inputs
    test_cases = [
        "test",
        "my-corpus",
        "projects/my-project/locations/us-central1/ragCorpora/existing-corpus",
        "partial/path/corpus-name"
    ]
    
    print("\nTesting multiple cases:")
    for test_case in test_cases:
        result = get_corpus_resource_name(test_case)
        print(f"'{test_case}' -> '{result}'")
