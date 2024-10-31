"""Status display component"""
import streamlit as st
from typing import List, Dict
from datetime import datetime

from core.logging import get_logger
from utils.helpers import format_currency
from utils.db_utils import get_records

logger = get_logger(__name__)

def status_section():
    """Status section of the application"""
    st.header("Processing Status")
    
    try:
        # Get recent extractions with order
        extractions = get_records(
            "pdf_extractions",
            order={"extracted_at": "desc"},
            limit=10
        )
        
        if not extractions:
            st.info("No extractions found. Upload some documents to get started.")
            return
            
        # Create DataFrame
        data = []
        for ext in extractions:
            data.append({
                "File": ext["file_name"],
                "Status": ext["status"],
                "Extracted At": ext.get("extracted_at", "N/A")
            })
        
        if data:
            st.dataframe(
                data,
                column_config={
                    "File": st.column_config.TextColumn(
                        "File Name",
                        width="large"
                    ),
                    "Status": st.column_config.Column(
                        "Status",
                        width="medium",
                        help="Processing status"
                    ),
                    "Extracted At": st.column_config.DatetimeColumn(
                        "Processed At",
                        format="DD/MM/YYYY HH:mm:ss",
                        width="medium"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error loading status: {str(e)}")
        logger.error("Error in status section", exc_info=e) 