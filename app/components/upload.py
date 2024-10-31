"""Upload component for document processing"""
import streamlit as st
from typing import List, Optional, Dict
from datetime import datetime

from core.logging import get_logger
from core.exceptions import PDFError, ValidationError, DatabaseError, ExtractionError
from models.db.extraction import PDFExtraction
from services.document_processor import document_processor
from repositories.extraction import extraction_repository

logger = get_logger(__name__)

def handle_upload(uploaded_file) -> Optional[Dict]:
    """Handle file upload with proper error handling and status tracking"""
    try:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            extraction = document_processor.process_document(
                content=uploaded_file.getvalue(),
                filename=uploaded_file.name
            )
            saved_extraction = extraction_repository.create_extraction(extraction)
            st.success(f"Successfully processed {uploaded_file.name}")
            # Switch to status tab automatically
            st.session_state.active_tab = "Status"
            return saved_extraction
    except PDFError as pe:
        st.error(f"PDF Error: {str(pe)}")
        logger.error(f"PDF processing failed", exc_info=pe)
    except ExtractionError as ee:
        st.error(f"Extraction Error: {str(ee)}")
        logger.error(f"LLM extraction failed", exc_info=ee)
    except DatabaseError as de:
        st.error(f"Database Error: {str(de)}")
        logger.error(f"Database operation failed", exc_info=de)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error during processing", exc_info=e)
    return None

def upload_section():
    """Handle file upload section"""
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Select one or more PDF invoice files to process"
    )
    
    if uploaded_files:
        with st.spinner('Processing files...'):
            extraction_results = []
            for uploaded_file in uploaded_files:
                result = handle_upload(uploaded_file)
                if result:
                    extraction_results.append(result)
            
            if extraction_results:
                st.success(f"Successfully processed {len(extraction_results)} files")
                # Provide feedback and guidance
                st.info("👉 Check the Status tab to view processing results")