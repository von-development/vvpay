"""Validation component"""
import streamlit as st
from typing import List, Dict
from datetime import datetime

from core.logging import get_logger
from services.validation_service import validation_service
from utils.db_utils import get_records
from app.utils.formatters import format_currency, get_payment_type_color, format_validation_errors

logger = get_logger(__name__)

def validation_section():
    """Validation section of the application"""
    st.header("🔍 Validation")
    
    try:
        # Get all extractions
        extractions = get_records(
            "pdf_extractions",
            order={"extracted_at": "desc"}
        )
        
        if not extractions:
            st.info("No documents available for validation.")
            return

        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        
        total = len(extractions)
        pending = len([e for e in extractions if e.get('status') == 'extracted'])
        validated = len([e for e in extractions if e.get('status') == 'validated'])
        
        with col1:
            st.metric("Total Documents", total)
        with col2:
            st.metric("Pending Validation", pending)
        with col3:
            st.metric("Validated", validated)

        # Show validation table
        if extractions:
            st.subheader("Documents for Validation")
            
            # Prepare data for display
            data = []
            for ext in extractions:
                data.append({
                    "File": ext["file_name"],
                    "Provider": ext["payee_name"],
                    "Amount": format_currency(ext["valor"]),
                    "Type": ext["payment_type"],
                    "Status": ext["status"],
                    "Confidence": f"{float(ext.get('confidence_score', 0)) * 100:.1f}%"
                })

            # Display as dataframe with formatting
            st.dataframe(
                data,
                column_config={
                    "File": st.column_config.TextColumn(
                        "Document",
                        width="large",
                        help="Document filename"
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
                    "Status": st.column_config.TextColumn(
                        "Status",
                        width="small"
                    ),
                    "Confidence": st.column_config.TextColumn(
                        "Confidence",
                        width="small"
                    )
                },
                hide_index=True,
                use_container_width=True
            )

        # Validation actions
        if pending > 0:
            st.divider()
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"🔍 {pending} documents pending validation")
            
            with col2:
                if st.button("Validate All", type="primary"):
                    with st.spinner("Validating documents..."):
                        try:
                            results = validation_service.validate_all_pending()
                            st.success(f"Successfully validated {len(results)} documents")
                            st.rerun()  # Refresh the page
                        except Exception as e:
                            st.error(f"Validation failed: {str(e)}")
                            logger.error("Validation failed", exc_info=e)
        
        # Show validation history if available
        validation_results = get_records(
            "validation_results",
            order={"validated_at": "desc"},
            limit=5
        )
        
        if validation_results:
            st.divider()
            st.subheader("Recent Validations")
            for result in validation_results:
                with st.expander(f"Validation {result['id'][:8]}", expanded=False):
                    st.write(f"**Status:** {result['status']}")
                    st.write(f"**Validated At:** {result['validated_at']}")
                    if result.get('validation_errors'):
                        st.error(format_validation_errors(result['validation_errors']))
                    
    except Exception as e:
        st.error(f"Error loading validation data: {str(e)}")
        logger.error("Error in validation section", exc_info=e) 