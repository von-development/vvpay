"""Validation component"""
import streamlit as st
from typing import List, Dict
from datetime import datetime

from core.logging import get_logger
from services.validation_service import validation_service
from repositories.validation import validation_repository
from utils.db_utils import get_records
from app.utils.formatters import (
    format_currency,
    format_validation_errors,
    get_validation_status_display,
    format_datetime
)

logger = get_logger(__name__)

def show_document_table(documents: List[Dict], title: str, show_actions: bool = False):
    """Display document table with consistent formatting"""
    if not documents:
        return
        
    st.subheader(title)
    
    # Prepare data for table
    data = []
    for doc in documents:
        data.append({
            "Document": doc["file_name"],
            "Provider": doc["payee_name"],
            "Amount": format_currency(doc["valor"]),
            "Type": doc["payment_type"].upper(),
            "Confidence": f"{float(doc.get('confidence_score', 0)) * 100:.1f}%",
            "Processed": format_datetime(doc.get("extracted_at", "N/A"))
        })
    
    # Display table
    st.dataframe(
        data,
        column_config={
            "Document": st.column_config.TextColumn(
                "Document",
                width="large",
            ),
            "Provider": st.column_config.TextColumn(
                "Provider",
                width="medium"
            ),
            "Amount": st.column_config.TextColumn(
                "Amount",
                width="small"
            ),
            "Type": st.column_config.TextColumn(
                "Type",
                width="small"
            ),
            "Confidence": st.column_config.TextColumn(
                "Confidence",
                width="small"
            ),
            "Processed": st.column_config.TextColumn(
                "Processed At",
                width="medium"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    if show_actions and data:
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"🔍 {len(data)} documents pending validation")
        with col2:
            if st.button("Validate All", type="primary"):
                with st.spinner("Validating documents..."):
                    try:
                        results = validation_service.validate_all_pending()
                        st.success(f"Successfully validated {len(results)} documents")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Validation failed: {str(e)}")
                        logger.error("Validation failed", exc_info=e)

def validation_section():
    """Validation section of the application"""
    st.header("🔍 Document Validation")
    
    try:
        # Get all extractions
        extractions = get_records(
            "pdf_extractions",
            order={"field": "extracted_at", "direction": "desc"}
        )
        
        if not extractions:
            st.info("No documents available for validation.")
            return
        
        # Group documents by status
        pending = [e for e in extractions if e.get('status') == 'extracted']
        validated = [e for e in extractions if e.get('status') == 'validated']
        failed = [e for e in extractions if e.get('status') == 'failed']
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Documents", len(extractions))
        with col2:
            st.metric("Pending", len(pending), delta=f"{len(pending)} to validate")
        with col3:
            st.metric("Validated", len(validated))
        with col4:
            st.metric("Failed", len(failed), delta=f"{len(failed)} errors")
        
        # Display document tables
        st.divider()
        
        # Pending documents (with validation actions)
        if pending:
            show_document_table(pending, "📋 Pending Documents", show_actions=True)
            
        # Validated documents
        if validated:
            st.divider()
            show_document_table(validated, "✅ Validated Documents")
            
        # Failed documents
        if failed:
            st.divider()
            show_document_table(failed, "❌ Failed Documents")
                    
    except Exception as e:
        st.error(f"Error loading validation data: {str(e)}")
        logger.error("Error in validation section", exc_info=e)