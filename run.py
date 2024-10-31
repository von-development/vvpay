"""Launcher script for Streamlit app"""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import and run Streamlit app
from app.main import main

if __name__ == "__main__":
    main() 