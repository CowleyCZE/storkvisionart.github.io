"""OAuth 2.0 PKCE helper utilities for Etsy Open API v3.

This module provides functions to generate PKCE code verifier/challenge,
build an authorization URL and exchange an authorization code for tokens.

Notes:
- Etsy OAuth endpoints used here are suitable for v3 integration.
  Adjust constants if Etsy updates endpoints.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import urllib.parse
from typing import Iterable, Optional

import requests

# OAuth endpoints (Etsy v3)
AUTHORIZATION_BASE_URL = "https://www.etsy.com/oauth/connect"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"


def generate_code_verifier(length: int = 128) -> str:
    """Generate a URL-safe code verifier string.

    RFC 7636 recommends a length between 43 and 128 characters.
    """
    if length < 43 or length > 128:
        raise ValueError("code_verifier length must be between 43 and 128")
    # secrets.token_urlsafe may produce slightly longer strings; trim if needed
    verifier = secrets.token_urlsafe(length)
    return verifier[:length]


def generate_code_challenge(code_verifier: str) -> str:
    """Create a base64url-encoded SHA256 code_challenge from code_verifier."""
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return challenge


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    scopes: Iterable[str],
    code_challenge: str,
    state: Optional[str] = None,
) -> str:
    """Construct the OAuth2 authorization URL for the user to visit.

    Parameters:
    - client_id: Etsy app key (API key)
    - redirect_uri: Registered redirect URI
    - scopes: Iterable of scope strings
    - code_challenge: PKCE S256 challenge string
    - state: Optional CSRF state string
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if state:
        params["state"] = state

    url = AUTHORIZATION_BASE_URL + "?" + urllib.parse.urlencode(params)
    return url


def exchange_code_for_tokens(
    client_id: str,
    client_secret: Optional[str],
    code: str,
    redirect_uri: str,
    code_verifier: str,
) -> dict:
    """Exchange the authorization code for access (and refresh) tokens.

    Returns the parsed JSON response from the token endpoint.
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    # If a client secret is available (confidential client), include it.
    if client_secret:
        data["client_secret"] = client_secret

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(
    client_id: str, client_secret: Optional[str], refresh_token: str
) -> dict:
    """Refresh access token using a refresh token.

    Returns the parsed JSON response containing a new access token.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()
