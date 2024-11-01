"""Status display component"""
import streamlit as st
from typing import List, Dict
from datetime import datetime

from core.logging import get_logger
from utils.helpers import format_currency
from utils.db_utils import get_records
from app.utils.formatters import get_validation_status_display, format_datetime

logger = get_logger(__name__)

def status_section():
    """Status section of the application"""
    st.header("📊 Processing Status")
    
    try:
        # Get recent extractions with order
        extractions = get_records(
            "pdf_extractions",
            order={"field": "extracted_at", "direction": "desc"},
            limit=10
        )
        
        if not extractions:
            st.info("No extractions found. Upload some documents to get started.")
            return
        
        # Display metrics
        total = len(extractions)
        extracted = len([e for e in extractions if e.get('status') == 'extracted'])
        validated = len([e for e in extractions if e.get('status') == 'validated'])
        failed = len([e for e in extractions if e.get('status') == 'failed'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Documents", total)
        with col2:
            st.metric("Pending", extracted, delta=f"{extracted} pending")
        with col3:
            st.metric("Validated", validated, delta=f"{validated} processed")
        with col4:
            st.metric("Failed", failed, delta=f"{failed} errors")
            
        # Create status table
        st.subheader("Recent Documents")
        
        # Prepare data for table
        data = []
        for ext in extractions:
            data.append({
                "Document": ext["file_name"],
                "Provider": ext["payee_name"],
                "Amount": format_currency(ext["valor"]),
                "Status": ext["status"],
                "Processed": format_datetime(ext.get("extracted_at", "N/A"))
            })
            
        # Display as table
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
                "Status": st.column_config.TextColumn(
                    "Status",
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
                    
    except Exception as e:
        st.error(f"Error loading status: {str(e)}")
        logger.error("Error in status section", exc_info=e) 