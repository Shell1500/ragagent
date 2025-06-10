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


def get_corpus_resource_name() -> str:
    return "projects/gen-lang-client-0516570023/locations/us-central1/ragCorpora/4532873024948404224"
