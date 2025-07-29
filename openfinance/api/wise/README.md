# Wise Open Banking API

This module implements the OAuth2 authorization flow for Wise's Open Banking API according to the Open Banking standards.

## Features

- OAuth2 authorization flow with JWT request objects
- Support for all required parameters: `response_type`, `redirect_uri`, `scope`, `client_id`, `request`, `state`, `nonce`
- Token exchange functionality
- Session management for state validation
- Health check and scope information endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Wise API credentials:
```env
WISE_CLIENT_ID=your_client_id_here
WISE_CLIENT_SECRET=your_client_secret_here
WISE_REDIRECT_URI=http://localhost:5000/callback
FLASK_SECRET_KEY=your_secret_key_here
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

### GET /authorize
Initiates the OAuth2 authorization flow.

**Query Parameters:**
- `scope` (optional): Space-separated list of scopes (default: "openid accounts")
- `state` (optional): CSRF protection parameter
- `nonce` (optional): Replay attack protection parameter

**Response:**
```json
{
  "authorization_url": "https://sandbox.transferwise.tech/openbanking/authorize?...",
  "state": "generated_state",
  "nonce": "generated_nonce"
}
```

### GET /callback
Handles the OAuth2 callback from Wise.

**Query Parameters:**
- `code`: Authorization code from Wise
- `state`: State parameter for validation
- `id_token`: ID token from Wise
- `error` (optional): Error code if authorization failed
- `error_description` (optional): Error description

### GET /health
Health check endpoint.

### GET /scopes
Returns list of supported scopes.

## Supported Scopes

- `openid`: OpenID Connect authentication
- `accounts`: Account information access
- `payments`: Payment initiation
- `fundsconfirmations`: Funds confirmation
- `offline_access`: Offline access token

## JWT Request Object

The implementation creates a JWT request object as required by Wise's Open Banking API with the following claims:

- `iss`: Client ID (issuer)
- `aud`: Wise sandbox URL (audience)
- `response_type`: "code id_token"
- `client_id`: Client ID
- `redirect_uri`: Pre-registered redirect URI
- `scope`: Requested scopes
- `iat`: Issued at timestamp
- `exp`: Expiration timestamp (5 minutes)
- `jti`: Unique request identifier
- `state`: State parameter (if provided)
- `nonce`: Nonce parameter (if provided)

## Security Notes

1. **JWT Signing**: The current implementation uses a placeholder for JWT signing. In production, you must implement proper RS256 signing with your private key.

2. **Token Storage**: Tokens are stored in Flask sessions for demonstration. In production, implement secure token storage.

3. **State Validation**: The implementation validates the state parameter to prevent CSRF attacks.

4. **Environment Variables**: Always use environment variables for sensitive configuration.

## Example Usage

```python
import requests

# Initiate authorization
response = requests.get('http://localhost:5000/authorize', params={
    'scope': 'openid accounts payments'
})

auth_data = response.json()
print(f"Authorization URL: {auth_data['authorization_url']}")

# After user completes authorization, handle callback
# The callback will exchange the code for tokens automatically
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Missing required parameters or validation errors
- `500 Internal Server Error`: Server-side errors during processing

## Production Considerations

1. Implement proper JWT signing with your private key
2. Use secure token storage (database, encrypted storage)
3. Implement proper logging and monitoring
4. Add rate limiting and request validation
5. Use HTTPS in production
6. Implement proper error handling and user feedback 