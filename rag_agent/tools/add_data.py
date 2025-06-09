"""
Tool for adding new data sources to a Vertex AI RAG corpus.
"""

import re
from typing import List

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from ..config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
)
from .utils import check_corpus_exists, get_corpus_resource_name

from ..config import (
    LOCATION,
    PROJECT_ID,
)
MODEL_ID = "gemini-2.0-flash"
MODEL_NAME = "projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}"
MAX_PARSING_REQUESTS_PER_MIN = 1000
CUSTOM_PARSING_PROMPT = """
You are an expert document processing assistant specializing in extracting and converting PDF content into clean, structured text suitable for Retrieval-Augmented Generation (RAG) systems.
Your Task
Extract ALL textual content from the provided PDF document and convert it into clean, well-structured plain text that preserves the semantic meaning and logical flow of information.
Processing Instructions 
1. Content Extraction

Extract all visible text including body text, headers, footers, captions, footnotes, and annotations
Process scanned documents by performing OCR on any image-based text
Handle tables by converting them into structured text format using clear delimiters
Extract text from images including charts, diagrams, and infographics where text is present
Describe visual content by providing detailed descriptions of images, charts, graphs, diagrams, and illustrations that contain no text but convey important information
Preserve mathematical formulas and convert them to readable text format when possible
Include metadata such as document title, author, and creation date if visible

2. Text Cleaning and Formatting

Remove unnecessary formatting artifacts (page numbers, headers/footers if repetitive)
Fix OCR errors and typos where contextually obvious
Normalize spacing and line breaks
Convert special characters to standard text equivalents
Preserve intentional formatting like bullet points and numbered lists
Maintain paragraph structure and logical text flow

3. Structure Preservation

Headers and Sections: Clearly mark document sections with appropriate hierarchy
Lists: Convert to clean bulleted or numbered format
Tables: Present in readable text format with clear column/row separation
References: Preserve citation information and bibliography
Captions: Include image/table captions with context
Visual Elements: Provide descriptive text for images, charts, graphs, diagrams, and illustrations using format: [IMAGE: detailed description of visual content, including key information, data trends, or concepts depicted]

4. Quality Assurance

Ensure no content is lost or omitted
Verify text coherence and readability
Check that technical terms and proper nouns are correctly extracted
Maintain the original document's informational integrity

Output Format
Provide the extracted content as clean, structured plain text with:

Clear section breaks
Preserved logical flow
Consistent formatting
No extraneous markup or artifacts

Special Handling

Multi-column layouts: Read in logical order (left-to-right, top-to-bottom)
Forms: Extract field names and any filled-in content
Handwritten text: Attempt to transcribe if legible
Multiple languages: Preserve original language content
Technical documents: Maintain precision of technical terminology
Visual Content: For images without text, provide comprehensive descriptions that capture the essential information, data relationships, or concepts they represent

Error Handling
If any content is unclear, illegible, or potentially misinterpreted, note this with [UNCLEAR: description] tags rather than guessing.
"""


def add_data(
    corpus_name: str,
    paths: List[str],
    tool_context: ToolContext,
) -> dict:
    """
    Add new data sources to a Vertex AI RAG corpus.

    Args:
        corpus_name (str): The name of the corpus to add data to. If empty, the current corpus will be used.
        paths (List[str]): List of URLs or GCS paths to add to the corpus.
                          Supported formats:
                          - Google Drive: "https://drive.google.com/file/d/{FILE_ID}/view"
                          - Google Docs/Sheets/Slides: "https://docs.google.com/{type}/d/{FILE_ID}/..."
                          - Google Cloud Storage: "gs://{BUCKET}/{PATH}"
                          Example: ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir"]
        tool_context (ToolContext): The tool context

    Returns:
        dict: Information about the added data and status
    """
    # Check if the corpus exists
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' does not exist. Please create it first using the create_corpus tool.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Validate inputs
    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Invalid paths: Please provide a list of URLs or GCS paths",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    # Pre-process paths to validate and convert Google Docs URLs to Drive format if needed
    validated_paths = []
    invalid_paths = []
    conversions = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (Not a valid string)")
            continue

        # Check for Google Docs/Sheets/Slides URLs and convert them to Drive format
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} → {drive_url}")
            continue

        # Check for valid Drive URL format
        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if drive_match:
            # Normalize to the standard Drive URL format
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} → {drive_url}")
            continue

        # Check for GCS paths
        if path.startswith("gs://"):
            validated_paths.append(path)
            continue

        # If we're here, the path wasn't in a recognized format
        invalid_paths.append(f"{path} (Invalid format)")

    # Check if we have any valid paths after validation
    if not validated_paths:
        return {
            "status": "error",
            "message": "No valid paths provided. Please provide Google Drive URLs or GCS paths.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }

    try:
        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Set up chunking configuration
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )
        
        llm_parser_config = rag.LlmParserConfig(
            model_name = MODEL_NAME,
            max_parsing_requests_per_min=MAX_PARSING_REQUESTS_PER_MIN, # Optional
            custom_parsing_prompt=CUSTOM_PARSING_PROMPT, # Optional
        )

        # Import files to the corpus
        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            llm_parser=llm_parser_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )

        # Set this as the current corpus if not already set
        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        # Build the success message
        conversion_msg = ""
        if conversions:
            conversion_msg = " (Converted Google Docs URLs to Drive format)"

        return {
            "status": "success",
            "message": f"Successfully added {import_result.imported_rag_files_count} file(s) to corpus '{corpus_name}'{conversion_msg}",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
            "conversions": conversions,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding data to corpus: {str(e)}",
            "corpus_name": corpus_name,
            "paths": paths,
        }
