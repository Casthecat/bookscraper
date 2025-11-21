import requests
import time
import random
from typing import Optional

# Configuration for Robustness
MAX_RETRIES = 3      # Maximum number of times to retry a failed request
BACKOFF_FACTOR = 2.0 # Multiplier for the wait time during exponential backoff
REQUEST_TIMEOUT = 10 # Timeout for each request in seconds
# Note: User-Agent has been moved to main.py or is expected to be imported
USER_AGENT = 'BlueberryAI-Intern-Scraper (Contact: lindddkas@gmail.com)' 

def fetch_page(url: str, delay_ms: int) -> Optional[str]:
    """
    Fetches the HTML content of a URL, implementing polite delay and retry logic.
    
    Args:
        url: The target URL to fetch.
        delay_ms: The base delay time in milliseconds (from main.py argument).
        
    Returns:
        The HTML content (str) if successful, otherwise None.
    """
    
    # Convert milliseconds to seconds for time.sleep
    base_delay_sec = delay_ms / 1000.0
    
    # Define standard headers including the custom User-Agent
    headers = {'User-Agent': USER_AGENT}

    for attempt in range(1, MAX_RETRIES + 1):
        
        # Calculate Wait Time (Polite Delay OR Backoff) ---
        if attempt == 1:
            # First attempt: apply polite delay with random jitter (+/- 50% of base delay)
            jitter = random.uniform(-0.5 * base_delay_sec, 0.5 * base_delay_sec)
            wait_time = max(0.1, base_delay_sec + jitter) # Ensure wait time is not negative
        else:
            # Subsequent attempts: apply exponential backoff
            wait_time = base_delay_sec * (BACKOFF_FACTOR ** (attempt - 1))
        
        print(f"Attempt {attempt}/{MAX_RETRIES}. Waiting for {wait_time:.2f}s before fetching...")
        time.sleep(wait_time)
        
        try:
            # Send the HTTP GET request
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            # Check Status Code
            if response.status_code == 200:
                print(f"Successfully fetched {url}")
                
                # --- FIX FOR GARBLED CHARACTERS (乱码) ---
                # Explicitly set encoding to UTF-8 to prevent 'requests' from guessing wrong
                # and causing symbols (like '£' being read as 'Â£') to appear garbled.
                response.encoding = 'utf-8' 
                
                return response.text
            
            # Non-recoverable errors (e.g., 404 Not Found, 403 Forbidden). Abort.
            elif response.status_code in [403, 404]:
                print(f"Permanent error {response.status_code}. Aborting fetch for {url}.")
                return None
            
            # Recoverable errors (e.g., 429 Too Many Requests, 5xx Server Errors). Retry.
            elif response.status_code in [429, 500, 502, 503, 504]:
                print(f"Server reported status {response.status_code}. Retrying...")
                # Loop continues to the next attempt with increased backoff
            
            # Other status codes: treat as non-recoverable
            else:
                 print(f"Unexpected status code {response.status_code}. Aborting fetch for {url}.")
                 return None
                
        except requests.exceptions.RequestException as e:
            # Handle all network-related exceptions (e.g., timeouts, connection errors)
            print(f"Network error on attempt {attempt}: {e}. Retrying...")
            # Loop continues to the next attempt with backoff
            
    # If the loop finishes without success after all retries
    print(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")
    return None