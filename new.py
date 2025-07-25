+42
-60

import requests
from datetime import datetime
from urllib.parse import urlparse


def fetch_condition_id_from_slug(slug: str) -> str | None:
    """Return the condition ID for a market slug using the CLOB API."""
    url = f"https://clob.polymarket.com/simplified-markets?market_slug={slug}"
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        data = payload.get("data") or []
        if data:
            cid = data[0].get("condition_id")
            if cid:
                print(f"Fetched condition ID from clob API: {cid}")
                return cid
    except Exception as exc:
        print(f"CLOB API error: {exc}")
    return None

def polymarket_url_to_condition_id(polymarket_url):
    """Return the market's condition ID using the CLOB API.

    Args:
        polymarket_url (str): Polymarket event URL

    Returns:
        str | None: condition ID if found, otherwise ``None``.
    """
    parsed = urlparse(polymarket_url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) < 2 or path_parts[0] != 'event':
        raise ValueError("Invalid Polymarket URL format")

    event_slug = path_parts[1]

    print(f"Looking up slug '{event_slug}' via CLOB API...")
    cid = fetch_condition_id_from_slug(event_slug)
    if cid:
        return cid
    print("Failed to fetch condition ID from CLOB API")
    return None