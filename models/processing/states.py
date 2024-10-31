"""State management models for LLM processing flow"""
from typing import TypedDict, Dict, Optional, List

class GraphState(TypedDict):
    """
    Represents the state of the invoice processing graph.
    
    Attributes:
        file_name: Name of the PDF file
        content: Raw PDF content in bytes
        raw_text: Extracted text from PDF
        llm_analysis: First LLM analysis of the invoice
        json_output: Final structured JSON data
        error: Error message if any step fails
        documents: List of document chunks
    """
    file_name: str
    content: bytes
    raw_text: Optional[str]
    llm_analysis: Optional[str]
    json_output: Optional[Dict]
    error: Optional[str]
    documents: List[str]

def create_initial_state(filename: str, content: bytes) -> GraphState:
    """Create initial state for processing graph"""
    return {
        "file_name": filename,
        "content": content,
        "raw_text": None,
        "documents": [],
        "llm_analysis": None,
        "json_output": None,
        "error": None
    }