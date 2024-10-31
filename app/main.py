"""
vPay - Automated Payment Processing Application
Main Streamlit application file
"""
import streamlit as st

from core.config import settings
from core.logging import get_logger
from app.components.upload import upload_section
from app.components.status import status_section
from app.components.validation import validation_section

logger = get_logger(__name__)

def setup_page():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title=f"{settings.PROJECT_NAME} - Payment Processing",
        page_icon="💰",
        layout="wide"
    )
    
    st.title(f"{settings.PROJECT_NAME} - Payment Processing")

def main():
    """Main application function"""
    setup_page()
    
    # Initialize session state for active tab if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Upload"
    
    # Create tabs
    tabs = ["Upload", "Status", "Validation"]
    tab1, tab2, tab3 = st.tabs(tabs)
    
    # Show content in each tab without conditions
    with tab1:
        upload_section()
    
    with tab2:
        status_section()
    
    with tab3:
        validation_section()

if __name__ == "__main__":
    main() 