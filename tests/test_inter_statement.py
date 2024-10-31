import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import requests

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from config import INTER_CLIENT_ID, INTER_CLIENT_SECRET, INTER_CERT_FILE, INTER_KEY_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_token() -> str:
    """Get OAuth token for API access"""
    try:
        url = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"
        
        data = {
            "client_id": INTER_CLIENT_ID,
            "client_secret": INTER_CLIENT_SECRET,
            "scope": "extrato.read",
            "grant_type": "client_credentials"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(
            url,
            headers=headers,
            data=data,
            cert=(INTER_CERT_FILE, INTER_KEY_FILE),
            verify=True
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get token: {response.text}")
        
        return response.json().get("access_token")
        
    except Exception as e:
        logger.error(f"Error getting token: {str(e)}")
        raise

def test_get_statement():
    """Test getting account statement"""
    try:
        # First get token
        token = get_token()
        logger.info("Successfully obtained access token")
        
        # Set date range for first 15 days of October 2024
        start_date = datetime(2024, 10, 1)
        end_date = datetime(2024, 10, 15)
        
        # Prepare request
        url = "https://cdpj.partners.bancointer.com.br/banking/v2/extrato"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "dataInicio": start_date.strftime("%Y-%m-%d"),
            "dataFim": end_date.strftime("%Y-%m-%d")
        }
        
        # Make request
        logger.info(f"Requesting statement from {start_date.date()} to {end_date.date()}")
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cert=(INTER_CERT_FILE, INTER_KEY_FILE)
        )
        
        # Log response details
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            statement = response.json()
            transactions = statement.get("transacoes", [])
            logger.info(f"Successfully retrieved {len(transactions)} transactions")
            
            # Print transaction summary
            if transactions:
                logger.info("\nTransaction Summary:")
                logger.info("-" * 50)
                for tx in transactions:
                    logger.info(f"""
                    Date: {tx.get('dataEntrada')}
                    Type: {tx.get('tipoTransacao')}
                    Operation: {tx.get('tipoOperacao')}
                    Value: R$ {float(tx.get('valor', '0'))}
                    Title: {tx.get('titulo')}
                    Description: {tx.get('descricao')}
                    """)
                logger.info("-" * 50)
                
                # Calculate totals
                credits = sum(float(tx.get('valor', 0)) for tx in transactions if tx.get('tipoOperacao') == 'C')
                debits = sum(float(tx.get('valor', 0)) for tx in transactions if tx.get('tipoOperacao') == 'D')
                
                logger.info(f"\nSummary:")
                logger.info(f"Total Credits: R$ {credits:.2f}")
                logger.info(f"Total Debits: R$ {debits:.2f}")
                logger.info(f"Net Balance: R$ {credits - debits:.2f}")
            else:
                logger.info("No transactions found in the specified period")
                
        else:
            logger.error(f"Failed to get statement: {response.text}")
            
    except Exception as e:
        logger.error(f"Statement test failed: {str(e)}")

def test_date_range_validation():
    """Test statement date range validation"""
    try:
        token = get_token()
        url = "https://cdpj.partners.bancointer.com.br/banking/v2/extrato"
        
        # Test cases
        test_cases = [
            {
                "name": "Valid date range",
                "start": datetime(2024, 10, 1),
                "end": datetime(2024, 10, 15)
            },
            {
                "name": "Range > 90 days",
                "start": datetime(2024, 7, 1),
                "end": datetime(2024, 10, 15)
            },
            {
                "name": "End date before start date",
                "start": datetime(2024, 10, 15),
                "end": datetime(2024, 10, 1)
            }
        ]
        
        for case in test_cases:
            logger.info(f"\nTesting {case['name']}...")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "dataInicio": case['start'].strftime("%Y-%m-%d"),
                "dataFim": case['end'].strftime("%Y-%m-%d")
            }
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                cert=(INTER_CERT_FILE, INTER_KEY_FILE)
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"Date range validation test failed: {str(e)}")

if __name__ == "__main__":
    print("Running Inter API Statement Tests...")
    print("\n1. Testing Account Statement Retrieval:")
    test_get_statement()
    
    print("\n2. Testing Date Range Validation:")
    test_date_range_validation() 