"""
Tool for deleting a specific document from a Vertex AI RAG corpus.
"""

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from .utils import get_corpus_resource_name


def delete_document(
    document_id: str,
    tool_context: ToolContext,
) -> dict:
    """
    Delete a specific document from a Vertex AI RAG corpus.

    Args:
        document_id (str): The ID of the specific document/file to delete. This can be
                          obtained from get_corpus_info results.
        tool_context (ToolContext): The tool context

    Returns:
        dict: Status information about the deletion operation
    """
    try:
        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name()

        # Delete the document
        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        rag.delete_file(rag_file_path)

        return {
            "status": "success",
            "message": f"Successfully deleted document '{document_id}' from corpus 'hardcoded-corpus'",
            "corpus_name": "hardcoded-corpus",
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting document: {str(e)}",
            "corpus_name": "hardcoded-corpus",
            "document_id": document_id,
        }
