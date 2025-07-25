import requests
from datetime import datetime
from urllib.parse import urlparse

def polymarket_url_to_condition_id(polymarket_url):
    """
    Convert a Polymarket URL to condition ID using events API.
    
    Args:
        polymarket_url (str): Polymarket event URL
        
    Returns:
        str: First condition ID found, or None if none found
    """
    parsed = urlparse(polymarket_url)
    path_parts = parsed.path.strip('/').split('/')
    
    if len(path_parts) < 2 or path_parts[0] != 'event':
        raise ValueError("Invalid Polymarket URL format")
    
    event_slug = path_parts[1]
    
    print(f"Searching for event slug: '{event_slug}'")
    
    # Try strapi-matic API first (has archived events)
    try:
        strapi_url = f"https://strapi-matic.poly.market/events?slug={event_slug}"
        response = requests.get(strapi_url, timeout=5)
        if response.status_code == 200:
            events = response.json()
            if events and len(events) > 0:
                event = events[0]
                print(f"Found archived event: {event.get('title', 'Unknown title')}")
                markets = event.get('markets', [])
                if markets:
                    condition_id = markets[0].get('conditionId')
                    print(f"Extracted condition ID: {condition_id}")
                    return condition_id
    except requests.RequestException:
        print("Strapi API unavailable, trying Gamma API...")
    
    # Fallback to Gamma API using direct slug query
    try:
        gamma_url = f"https://gamma-api.polymarket.com/events?slug={event_slug}"
        response = requests.get(gamma_url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        if events and len(events) > 0:
            event = events[0]
            print(f"Found event: {event.get('title', 'Unknown title')}")
            markets = event.get('markets', [])
            if markets:
                condition_id = markets[0].get('conditionId')
                print(f"Extracted condition ID: {condition_id}")
                return condition_id
        
        print(f"Event '{event_slug}' not found.")
        return None
        
    except requests.RequestException as e:
        print(f"Gamma API error: {e}")
        return None

def get_recent_trades(condition_id, limit=50):
    """
    Get the most recent trades for a specific market.
    
    Args:
        condition_id (str): Market condition ID
        limit (int): Number of recent trades to fetch
        
    Returns:
        list: Recent trades data
    """
    try:
        params = {
            'market': condition_id,
            'limit': limit,
            'takerOnly': False  # Try including both maker and taker trades
        }
        
        response = requests.get("https://data-api.polymarket.com/trades", params=params)
        response.raise_for_status()
        
        trades = response.json()
        
        return trades
        
    except Exception as e:
        print(f"Error fetching trades: {e}")
        return []

def display_trades(trades):
    """Display trades in a clean format, skipping trades without usernames."""
    if not trades:
        print("No trades found")
        return
    
    # Filter out trades without usernames
    trades_with_usernames = []
    for trade in trades:
        username = trade.get("name") or trade.get("pseudonym")
        if username:
            trades_with_usernames.append(trade)
    
    if not trades_with_usernames:
        print("No trades with usernames found")
        return
    
    print(f"Most Recent {len(trades_with_usernames)} Trades (with usernames):")
    print("=" * 80)
    
    for i, trade in enumerate(trades_with_usernames, 1):
        username = trade.get("name") or trade.get("pseudonym")
        size = trade.get("size", 0)
        price = trade.get("price", 0)
        usdc_cost = size * price
        timestamp = datetime.fromtimestamp(trade.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{i}. {username}")
        print(f"   Trader: {trade.get('proxyWallet')}")
        print(f"   Amount: {size} shares")
        print(f"   Price: ${price}")
        print(f"   Cost: ${usdc_cost:.2f} USDC")
        print(f"   Side: {trade.get('side')}")
        print(f"   Time: {timestamp}")
        print()


if __name__ == "__main__":
    polymarket_url = input("Enter Polymarket URL: ")
    
    print("Extracting condition ID from URL...")
    condition_id = polymarket_url_to_condition_id(polymarket_url)
    
    if not condition_id:
        print("Failed to extract condition ID from URL.")
        exit(1)
    
    print("Fetching recent trades...")
    trades = get_recent_trades(condition_id, 50)
    display_trades(trades)