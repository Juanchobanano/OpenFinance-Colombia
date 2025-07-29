from flask import Flask, request, jsonify, session
import jwt
import uuid
import time
from urllib.parse import urlencode
import requests
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Wise Open Banking Configuration
WISE_SANDBOX_BASE_URL = "https://sandbox.transferwise.tech"
WISE_AUTHORIZE_URL = f"{WISE_SANDBOX_BASE_URL}/openbanking/authorize"
WISE_TOKEN_URL = f"{WISE_SANDBOX_BASE_URL}/openbanking/token"

# Configuration from environment variables
WISE_CLIENT_ID = os.getenv('WISE_CLIENT_ID')
WISE_CLIENT_SECRET = os.getenv('WISE_CLIENT_SECRET')
WISE_REDIRECT_URI = os.getenv(
    'WISE_REDIRECT_URI', 'http://localhost:5000/callback'
)

# Supported scopes for Wise Open Banking
SUPPORTED_SCOPES = [
    'openid',
    'accounts',
    'payments',
    'fundsconfirmations',
    'offline_access'
]


class WiseOpenBankingAPI:
    """Wise Open Banking API client for handling OAuth2 authorization flow"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def create_jwt_request_object(
        self, 
        scope: str, 
        state: Optional[str] = None, 
        nonce: Optional[str] = None
    ) -> str:
        """
        Create a JWT Request Object as required by Wise Open Banking API

        Args:
            scope: Space-separated list of requested scopes
            state: Optional state parameter for CSRF protection
            nonce: Optional nonce parameter for replay attack protection

        Returns:
            JWT encoded request object
        """
        # Create JWT header
        header = {
            "alg": "RS256",
            "typ": "JWT"
        }

        # Create JWT payload
        payload = {
            "iss": self.client_id,
            "aud": WISE_SANDBOX_BASE_URL,
            "response_type": "code id_token",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,  # 5 minutes expiration
            "jti": str(uuid.uuid4())  # Unique identifier for this request
        }

        # Add optional parameters if provided
        if state:
            payload["state"] = state
        if nonce:
            payload["nonce"] = nonce

        # Note: In a real implementation, you would sign this with your private key
        # For now, we'll use a placeholder - you'll need to implement proper JWT signing
        try:
            # This is a placeholder - replace with actual private key signing
            jwt_token = jwt.encode(
                payload,
                "your-private-key",
                algorithm="RS256",
                headers=header)
            return jwt_token
        except Exception as e:
            raise Exception(f"Failed to create JWT request object: {str(e)}")

    def build_authorization_url(
            self,
            scope: str,
            state: Optional[str] = None,
            nonce: Optional[str] = None) -> str:
        """
        Build the authorization URL for Wise Open Banking API

        Args:
            scope: Space-separated list of requested scopes
            state: Optional state parameter
            nonce: Optional nonce parameter

        Returns:
            Complete authorization URL
        """
        # Validate scope
        requested_scopes = scope.split()
        for s in requested_scopes:
            if s not in SUPPORTED_SCOPES:
                raise ValueError(f"Unsupported scope: {s}")

        # Create JWT request object
        request_jwt = self.create_jwt_request_object(scope, state, nonce)

        # Build query parameters
        params = {
            "response_type": "code id_token",
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "client_id": self.client_id,
            "request": request_jwt
        }

        # Add optional parameters
        if state:
            params["state"] = state
        if nonce:
            params["nonce"] = nonce

        # Build URL
        auth_url = f"{WISE_AUTHORIZE_URL}?{urlencode(params)}"
        return auth_url

    def exchange_code_for_token(
            self,
            authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            authorization_code: The authorization code received from Wise

        Returns:
            Token response containing access_token, id_token, etc.
        """
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(WISE_TOKEN_URL, data=token_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to exchange code for token: {str(e)}")


# Initialize the API client
wise_api = WiseOpenBankingAPI(
    WISE_CLIENT_ID, WISE_CLIENT_SECRET, WISE_REDIRECT_URI)


@app.route('/authorize', methods=['GET'])
def authorize():
    """
    Initiate OAuth2 authorization flow with Wise Open Banking API
    """
    try:
        # Get parameters from request
        scope = request.args.get('scope', 'openid accounts')
        state = request.args.get('state')
        nonce = request.args.get('nonce')

        # Validate required parameters
        if not scope:
            return jsonify({"error": "scope parameter is required"}), 400

        # Generate state and nonce if not provided
        if not state:
            state = str(uuid.uuid4())
        if not nonce:
            nonce = str(uuid.uuid4())

        # Store state and nonce in session for validation
        session['oauth_state'] = state
        session['oauth_nonce'] = nonce

        # Build authorization URL
        auth_url = wise_api.build_authorization_url(scope, state, nonce)

        return jsonify({
            "authorization_url": auth_url,
            "state": state,
            "nonce": nonce
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/callback', methods=['GET'])
def callback():
    """
    Handle the OAuth2 callback from Wise Open Banking API
    """
    try:
        # Get parameters from callback
        code = request.args.get('code')
        state = request.args.get('state')
        _ = request.args.get('id_token')
        error = request.args.get('error')
        error_description = request.args.get('error_description')

        # Check for errors
        if error:
            return jsonify({
                "error": error,
                "error_description": error_description
            }), 400

        # Validate required parameters
        if not code:
            return jsonify({"error": "Authorization code is required"}), 400

        # Validate state parameter
        stored_state = session.get('oauth_state')
        if state != stored_state:
            return jsonify({"error": "Invalid state parameter"}), 400

        # Exchange code for token
        token_response = wise_api.exchange_code_for_token(code)

        # Store tokens in session (in production, store securely)
        session['access_token'] = token_response.get('access_token')
        session['id_token'] = token_response.get('id_token')
        session['refresh_token'] = token_response.get('refresh_token')

        return jsonify({
            "message": "Authorization successful",
            "access_token": token_response.get('access_token'),
            "token_type": token_response.get('token_type'),
            "expires_in": token_response.get('expires_in'),
            "scope": token_response.get('scope')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Wise Open Banking API"})


@app.route('/scopes', methods=['GET'])
def get_supported_scopes():
    """Get list of supported scopes"""
    return jsonify({
        "supported_scopes": SUPPORTED_SCOPES,
        "description": "Available scopes for Wise Open Banking API"
    })


if __name__ == '__main__':
    # Validate required environment variables
    if not WISE_CLIENT_ID:
        print("Warning: WISE_CLIENT_ID not set in environment variables")
    if not WISE_CLIENT_SECRET:
        print("Warning: WISE_CLIENT_SECRET not set in environment variables")

    app.run(debug=True, host='0.0.0.0', port=8000)
