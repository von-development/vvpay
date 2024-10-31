import sys
from pathlib import Path
import logging
import requests

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from config import INTER_CLIENT_ID, INTER_CLIENT_SECRET, INTER_CERT_FILE, INTER_KEY_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test basic connection to Inter API"""
    try:
        # Log configuration (without sensitive data)
        logger.info("Testing Inter API connection...")
        logger.info(f"Using certificate: {INTER_CERT_FILE}")
        logger.info(f"Using key file: {INTER_KEY_FILE}")
        logger.info(f"Client ID length: {len(INTER_CLIENT_ID)}")
        
        # Test URL
        url = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"
        
        # Prepare request
        data = {
            "client_id": INTER_CLIENT_ID,
            "client_secret": INTER_CLIENT_SECRET,
            "scope": "extrato.read",
            "grant_type": "client_credentials"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make request with detailed logging
        logger.info("Making request to Inter API...")
        response = requests.post(
            url,
            headers=headers,
            data=data,
            cert=(INTER_CERT_FILE, INTER_KEY_FILE),
            verify=True
        )
        
        # Log response details
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response body: {response.text}")
        
        if response.status_code == 200:
            logger.info("Connection successful!")
            return response.json().get("access_token")
        else:
            logger.error(f"Connection failed: {response.text}")
            return None
            
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Run tests
    print("Running Inter API Tests...")
    test_connection() 