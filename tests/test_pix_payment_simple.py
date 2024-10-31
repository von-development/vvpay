import sys
from pathlib import Path
import logging
import requests
import json
from datetime import datetime

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from config import INTER_CLIENT_ID, INTER_CLIENT_SECRET, INTER_CERT_FILE, INTER_KEY_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pix_payment():
    """Test PIX payment following Inter API documentation"""
    try:
        # Step 1: Get token - Exactly as in documentation
        request_body = (
            f"client_id={INTER_CLIENT_ID}"
            f"&client_secret={INTER_CLIENT_SECRET}"
            f"&scope=pagamento-pix.write"  # Exact scope from docs
            f"&grant_type=client_credentials"
        )
        
        logger.info("Requesting access token...")
        response = requests.post(
            "https://cdpj.partners.bancointer.com.br/oauth/v2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cert=(INTER_CERT_FILE, INTER_KEY_FILE),
            data=request_body
        )
        
        # Log response details
        logger.info(f"Token Response Status: {response.status_code}")
        logger.info(f"Token Response: {response.text}")
        
        response.raise_for_status()
        token = response.json().get("access_token")
        logger.info("Successfully obtained access token")
        
        # Step 2: Make PIX payment - Exactly matching documentation format
        payment_data = {
            "valor": 1.23,  # Number format, not string
            "dataPagamento": "2024-11-10",  # YYYY-MM-DD format
            "descricao": "Pix com chave Pix teste",
            "destinatario": {
                "tipo": "CHAVE",
                "chave": "57276191000136"  # Your PIX key
            }
        }
        
        # Convert to JSON string
        payment_body = json.dumps(payment_data)
        
        # Headers exactly as in docs
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "Application/json"  # Note the capital A
        }
        
        logger.info("Making PIX payment request...")
        logger.info(f"Request URL: https://cdpj.partners.bancointer.com.br/banking/v2/pix")
        logger.info(f"Request Headers: {headers}")
        logger.info(f"Request Body: {payment_body}")
        
        response = requests.post(
            "https://cdpj.partners.bancointer.com.br/banking/v2/pix",
            headers=headers,
            cert=(INTER_CERT_FILE, INTER_KEY_FILE),
            data=payment_body  # Use data with json.dumps() result
        )
        
        # Log response
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        logger.info(f"Response Body: {response.text}")
        
        response.raise_for_status()
        
        # Expected response format:
        # {
        #     "tipoRetorno": "APROVACAO",
        #     "codigoSolicitacao": "c42f0787-02cb-4b31-827e-459ec9d7ece1",
        #     "dataPagamento": "2022-03-15",
        #     "dataOperacao": "2022-03-15"
        # }
        
        result = response.json()
        logger.info("\nPIX Payment Result:")
        logger.info(f"Return Type: {result.get('tipoRetorno')}")
        logger.info(f"Request Code: {result.get('codigoSolicitacao')}")
        logger.info(f"Payment Date: {result.get('dataPagamento')}")
        logger.info(f"Operation Date: {result.get('dataOperacao')}")
        
        return True
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Error making PIX payment: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing PIX Payment...")
    success = test_pix_payment()
    print(f"\nTest {'succeeded' if success else 'failed'}")