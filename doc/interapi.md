# Banco Inter API Documentation Summary

This document explains the main functionalities and requirements for using the Banco Inter API to access account statements and perform Pix payments.

## 1. General API Errors
These are standard errors returned by various API endpoints:

- **400 Bad Request**: Invalid request format.
- **403 Forbidden**: Authenticated request violates authorization rules.
- **404 Not Found**: Requested resource not found.
- **410 Gone**: The entity existed but was permanently removed.
- **500 Internal Server Error**: Unexpected condition while processing the request.
- **503 Service Unavailable**: The service may be under maintenance or outside working hours.
- **504 Gateway Timeout**: Service response took too long.

---

## 2. Account Statement Query
This method retrieves account statements for a specified period (up to 90 days).

- **Production Endpoint**: `https://cdpj.partners.bancointer.com.br/banking/v2/extrato`
- **Sandbox Endpoint**: `https://cdpj-sandbox.partners.uatinter.co/banking/v2/extrato` (for testing with fictitious data)

### Request Requirements
- **Scope**: `extrato.read`
- **Rate Limit**: 10 requests per minute

### Parameters
- **Query Parameters**:
  - `dataInicio` (required): Start date in `YYYY-MM-DD` format.
  - `dataFim` (required): End date in `YYYY-MM-DD` format.
- **Header Parameters**:
  - `x-conta-corrente`: Bank account number (required if more than one account is associated).

### Python Code Example for Account Statement
This example retrieves an account statement within a specified date range.

```python
import requests

# Step 1: Authentication to obtain access token
request_body = "client_id=<your_client_id>&client_secret=<your_client_secret>&scope=extrato.read&grant_type=client_credentials"
response = requests.post("https://cdpj.partners.bancointer.com.br/oauth/v2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         cert=('<certificate_file>.crt', '<public_key_file>.key'),
                         data=request_body)
token = response.json().get("access_token")

# Step 2: Fetching the account statement
opFiltros = {"dataInicio": "2024-04-01", "dataFim": "2024-04-05"}
headers = {"Authorization": "Bearer " + token, "x-conta-corrente": "<selected_account>", "Content-Type": "Application/json"}

response = requests.get("https://cdpj.partners.bancointer.com.br/banking/v2/extrato",
                        params=opFiltros,
                        headers=headers,
                        cert=('<certificate_file>.crt', '<public_key_file>.key'))
print("Account Statement =", response.json())


## 3. Pix Payment
This method allows for initiating a Pix payment or transfer using banking details, key, or Copy and Paste code.

- **Production Endpoint**: `https://cdpj.partners.bancointer.com.br/banking/v2/pix`
- **Sandbox Endpoint**: `https://cdpj-sandbox.partners.uatinter.co/banking/v2/pix` (for testing with fictitious data)

### Request Requirements
- **Scope**: `pagamento-pix.write`
- **Rate Limit**: 60 requests per minute (1 request per second)

### Parameters
- **Header Parameters**:
  - `x-id-idempotente`: Unique ID to ensure idempotency according to RFC4122.
  - `x-conta-corrente`: Bank account number (required if more than one account is associated).
- **Request Body** (JSON format):
  - `valor` (required): Amount of Pix payment.
  - `dataPagamento`: Payment date (default is the current date if not specified).
  - `descricao`: Payment description (up to 140 characters).
  - `destinatario`: Recipient information, specifying either a Pix key or banking details.

### Python Code Example for Pix Payment
This example performs a Pix payment to a specified Pix key and date.

```python
import requests
import json

# Step 1: Authentication to obtain access token
request_body = "client_id=<your_client_id>&client_secret=<your_client_secret>&scope=pagamento-pix.write&grant_type=client_credentials"
response = requests.post("https://cdpj.partners.bancointer.com.br/oauth/v2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         cert=('<certificate_file>.crt', '<public_key_file>.key'),
                         data=request_body)
token = response.json().get("access_token")

# Step 2: Sending the Pix payment
payment_body = json.dumps({
  "valor": "100.00",
  "descricao": "payment...",
  "dataPagamento": "2024-11-02",
  "destinatario": {
      "tipo": "CHAVE",
      "chave": "<recipient_pix_key>"
  }
})

headers = {"Authorization": "Bearer " + token, "x-conta-corrente": "<selected_account>", "Content-Type": "Application/json"}

response = requests.post("https://cdpj.partners.bancointer.com.br/banking/v2/pix",
                         headers=headers,
                         cert=('<certificate_file>.crt', '<public_key_file>.key'),
                         data=payment_body)
print("Pix Payment =", response.json())


- **Additional Notes**
- To use this API method, you need:

- Digital Certificates: Application certificate (.crt) and private key (.key).
- API Credentials: client_id and client_secret for your application.
- Access Token: Required to authenticate each request.