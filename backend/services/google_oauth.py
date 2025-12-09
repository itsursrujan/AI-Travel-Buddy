# backend/services/google_oauth.py
import os
import requests

from config import Config

TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

def verify_id_token(id_token: str) -> dict:
    """Verify Google ID token using Google's tokeninfo endpoint.

    Returns the token payload on success or raises ValueError on failure.
    """
    if not id_token:
        raise ValueError("id_token is required")

    params = {"id_token": id_token}
    resp = requests.get(TOKENINFO_URL, params=params, timeout=5)
    if resp.status_code != 200:
        raise ValueError(f"Invalid token: {resp.text}")

    payload = resp.json()

    # Optional client ID check
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or Config.GOOGLE_OAUTH_CLIENT_ID if hasattr(Config, 'GOOGLE_OAUTH_CLIENT_ID') else None
    if client_id and payload.get("aud") != client_id:
        raise ValueError("Token audience does not match CLIENT_ID")

    return payload
