import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

from config.settings import settings

logger = logging.getLogger(__name__)

class InterAPIError(Exception):
    """Custom exception for Inter API errors"""
    pass

class InterBankService:
    """Service for interacting with Banco Inter's API"""
    
    def __init__(self):
        self.base_url = "https://cdpj.partners.bancointer.com.br"
        self.token = None
        self.cert = (settings.INTER_CERT_FILE, settings.INTER_KEY_FILE)
        self.account_number = settings.INTER_ACCOUNT_NUMBER
        
    def _get_token(self, scope: str) -> str:
        """Get OAuth token for API access"""
        try:
            url = f"{self.base_url}/oauth/v2/token"
            
            data = {
                "client_id": settings.INTER_CLIENT_ID,
                "client_secret": settings.INTER_CLIENT_SECRET,
                "scope": scope,
                "grant_type": "client_credentials"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Log request details (without sensitive info)
            logger.info(f"Requesting token for scope: {scope}")
            logger.info(f"Using certificates: {self.cert}")
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                cert=self.cert,
                verify=True  # Ensure SSL verification
            )
            
            # Log response details
            logger.info(f"Token request status code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Token request failed: {response.text}")
                raise InterAPIError(f"Failed to get token: {response.text}")
            
            token_data = response.json()
            if 'access_token' not in token_data:
                raise InterAPIError("No access token in response")
                
            self.token = token_data['access_token']
            return self.token
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error: {str(e)}")
            raise InterAPIError(f"SSL Certificate error: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {str(e)}")
            raise InterAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            raise InterAPIError(f"Failed to get token: {str(e)}")
    
    def get_account_statement(
        self,
        start_date: datetime,
        end_date: datetime,
        account_number: Optional[str] = None
    ) -> Dict:
        """
        Get account statement for a specified period
        
        Args:
            start_date (datetime): Start date for statement
            end_date (datetime): End date for statement
            account_number (str, optional): Account number if multiple accounts exist
            
        Returns:
            Dict: Account statement data
        """
        try:
            # Get token with correct scope
            token = self._get_token("extrato.read")
            
            # Prepare request
            url = f"{self.base_url}/banking/v2/extrato"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Add account number if provided in parameters or settings
            if account_number or self.account_number:
                headers["x-conta-corrente"] = account_number or self.account_number
            
            # Format dates
            params = {
                "dataInicio": start_date.strftime("%Y-%m-%d"),
                "dataFim": end_date.strftime("%Y-%m-%d")
            }
            
            # Log request details
            logger.info(f"Requesting statement from {start_date} to {end_date}")
            
            # Make request
            response = requests.get(
                url,
                headers=headers,
                params=params,
                cert=self.cert
            )
            
            if response.status_code != 200:
                logger.error(f"Statement request failed: {response.text}")
                raise InterAPIError(f"Failed to get statement: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting account statement: {str(e)}")
            raise InterAPIError(f"Failed to get account statement: {str(e)}")

# Create singleton instance
inter_service = InterBankService() 