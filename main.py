"""Simple example CLI to perform OAuth PKCE flow and call
Etsy API endpoints.

Usage:
 - Fill `.env` (or export env vars) with the following keys:
     `ETSY_API_KEY`, `ETSY_SHARED_SECRET`, `ETSY_REDIRECT_URI`,
     `ETSY_SHOP_ID`.
 - Run `python main.py` and follow the interactive prompts.

This script is intentionally minimal and intended as a starting
point.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Optional

import importlib.util

# Import `load_dotenv` only if the `python-dotenv` package is available.
# Use a safe fallback when it's not installed to avoid runtime errors
# and to suppress language-server missing-import diagnostics.
if importlib.util.find_spec("dotenv") is not None:
    from dotenv import load_dotenv  # type: ignore
else:
    def load_dotenv() -> None:  # type: ignore[no-redef]
        """Fallback loader when `python-dotenv` is not available.

        In production or development you should install `python-dotenv`.
        """
        return None

import requests

from auth_helper import (
    generate_code_challenge,
    generate_code_verifier,
    build_authorization_url,
    exchange_code_for_tokens,
)


load_dotenv()

ETSY_API_KEY = os.getenv("ETSY_API_KEY")
ETSY_SHARED_SECRET = os.getenv("ETSY_SHARED_SECRET")
ETSY_REDIRECT_URI = os.getenv("ETSY_REDIRECT_URI")
ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

API_BASE = "https://api.etsy.com/v3/application"


def get_shop_details(access_token: str, shop_id: str) -> Optional[dict]:
    """Call GET /v3/application/shops/{shop_id} and return JSON.

    Basic error handling for HTTP errors is included.
    """
    url = f"{API_BASE}/shops/{shop_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        resp_obj = getattr(exc, "response", None)
        if resp_obj is not None:
            try:
                print("Response:", resp_obj.text, file=sys.stderr)
            except Exception:
                pass
        return None


def interactive_auth_flow() -> Optional[dict]:
    """Perform interactive PKCE authorization flow and exchange code for tokens.

    Steps:
    1. Generate code_verifier and code_challenge.
    2. Build authorization URL and instruct user to open it.
    3. User completes OAuth flow and pastes `code` from redirect URL.
    4. Exchange code for tokens and return token JSON.
    """
    if not ETSY_API_KEY or not ETSY_REDIRECT_URI:
        print("ETSY_API_KEY and ETSY_REDIRECT_URI must be set in environment.")
        return None

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    # Recommended scopes: only request the minimum needed for your app
    scopes = ["listings_r", "shops_r"]
    auth_url = build_authorization_url(
        ETSY_API_KEY,
        ETSY_REDIRECT_URI,
        scopes,
        code_challenge,
    )

    print("Open the following URL in your browser to authorize the")
    print("application:")
    print(auth_url)
    print("")
    print("After approving, you will be redirected to the redirect URI.")
    print("Copy the 'code' parameter from the URL and paste it below.")
    code = input("Paste authorization code: ").strip()
    if not code:
        print("No code provided, aborting.")
        return None

    try:
        tokens = exchange_code_for_tokens(
            ETSY_API_KEY,
            ETSY_SHARED_SECRET,
            code,
            ETSY_REDIRECT_URI,
            code_verifier,
        )
        print("Received tokens:")
        print(json.dumps(tokens, indent=2))
        print(
            "\nSave access_token and refresh_token securely (for example, "
            "in a secrets manager or a local .env file for development)."
        )
        return tokens
    except requests.exceptions.HTTPError as exc:
        print(f"Token exchange failed: {exc}", file=sys.stderr)
        resp_obj = getattr(exc, "response", None)
        if resp_obj is not None:
            try:
                print("Response:", resp_obj.text, file=sys.stderr)
            except Exception:
                pass
        return None


def main() -> int:
    # If an access token is already present in env, use it directly
    if ACCESS_TOKEN and ETSY_SHOP_ID:
        print("Using ACCESS_TOKEN from environment to fetch shop details...")
        data = get_shop_details(ACCESS_TOKEN, ETSY_SHOP_ID)
        if data:
            print(json.dumps(data, indent=2))
            return 0
        else:
            print("Failed to fetch shop details with provided ACCESS_TOKEN.")

    # Otherwise run interactive auth flow
    tokens = interactive_auth_flow()
    if not tokens:
        return 1

    access_token = tokens.get("access_token")

    if access_token and ETSY_SHOP_ID:
        print("Calling get_shop_details with new access token...")
        details = get_shop_details(access_token, ETSY_SHOP_ID)
        if details:
            print(json.dumps(details, indent=2))
            return 0

    print(
        "Done. If you want persistent tokens, save them into your .env "
        "or a secrets manager."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
