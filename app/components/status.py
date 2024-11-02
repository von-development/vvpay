"""Status display component"""
import streamlit as st
from typing import List, Dict
from datetime import datetime
import pandas as pd

from core.logging import get_logger
from utils.helpers import format_currency
from utils.db_utils import get_records
from services.validation_service import validation_service
from app.utils.formatters import format_currency, format_date, get_payment_type_color, get_status_color
from app.styles.theme import VALIDATION_COLORS, get_status_style

logger = get_logger(__name__)

def status_section():
    """Display status of document processing and validation"""
    try:
        st.header("Processing Status", divider="rainbow")
        
        # Get combined results
        results = validation_service.get_combined_validation_status()
        
        if not results:
            st.info("No documents have been processed yet.")
            return
            
        # Create DataFrame for display
        df = pd.DataFrame(results)
        
        # Add styling for payment types and status
        def style_payment_type(val):
            color = get_payment_type_color(val)
            return f'background-color: {color}; color: white; border-radius: 4px; padding: 2px 6px'
            
        def style_status(val):
            color = VALIDATION_COLORS.get(val, VALIDATION_COLORS["DEFAULT"])
            return f'background-color: {color}; color: white; border-radius: 4px; padding: 2px 6px'
        
        # Configure column display with enhanced styling
        st.dataframe(
            df,
            column_config={
                "payee_name": st.column_config.TextColumn(
                    "Payee Name",
                    width="medium",
                    help="Name of the payment recipient"
                ),
                "filename": st.column_config.TextColumn(
                    "File Name",
                    width="medium",
                    help="Original document filename"
                ),
                "cnpj": st.column_config.TextColumn(
                    "CNPJ",
                    width="small",
                    help="Company CNPJ"
                ),
                "payment_type": st.column_config.TextColumn(
                    "Payment Type",
                    width="small",
                    help="Type of payment"
                ),
                "competence": st.column_config.TextColumn(
                    "Competence",
                    width="small",
                    help="Payment competence period"
                ),
                "value": st.column_config.NumberColumn(
                    "Value",
                    format="R$ %.2f",
                    width="small",
                    help="Payment amount"
                ),
                "status": st.column_config.TextColumn(
                    "Status",
                    width="small",
                    help="Current validation status"
                ),
                "validation_date": st.column_config.DatetimeColumn(
                    "Validated At",
                    format="DD/MM/YY HH:mm",
                    width="small",
                    help="Date and time of validation"
                ),
                "is_valid": st.column_config.CheckboxColumn(
                    "Valid",
                    width="small",
                    help="Validation result"
                )
            },
            hide_index=True,
            use_container_width=True,
            column_order=[
                "payee_name", "cnpj", "payment_type", 
                "competence", "value", "status", 
                "is_valid", "validation_date"
            ]
        )
        
        # Add summary statistics with enhanced styling
        st.divider()
        
        # Summary metrics with custom styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valid_count = len([r for r in results if r.get("is_valid") is True])
            st.metric(
                "Valid Documents", 
                valid_count,
                delta=f"{valid_count/len(results)*100:.1f}%" if results else "0%",
                delta_color="normal"
            )
            
        with col2:
            invalid_count = len([r for r in results if r.get("is_valid") is False])
            st.metric(
                "Invalid Documents", 
                invalid_count,
                delta=f"{invalid_count/len(results)*100:.1f}%" if results else "0%",
                delta_color="inverse"
            )
            
        with col3:
            pending_count = len([r for r in results if r.get("is_valid") is None])
            st.metric(
                "Pending Documents", 
                pending_count,
                delta=f"{pending_count/len(results)*100:.1f}%" if results else "0%",
                delta_color="off"
            )

        # Add error details with improved styling
        if any(r.get("validation_errors") for r in results):
            st.divider()
            st.subheader("Validation Details 🔍")
            
            for result in results:
                if result.get("validation_errors"):
                    with st.expander(f"📄 {result['filename']}"):
                        for error in result["validation_errors"]:
                            st.error(
                                f"**{error['field'].title()}**: {error['error']}", 
                                icon="⚠️"
                            )

    except Exception as e:
        st.error(f"Error loading status: {str(e)}", icon="🚨")
        logger.error("Error in status section", exc_info=e)