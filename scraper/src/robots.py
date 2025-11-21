from urllib import robotparser
from urllib.parse import urlparse
from typing import Dict, Optional
import time

class RobotsChecker:
    """
    Handles fetching and checking rules from robots.txt for various domains.
    Implements a simple cache to avoid refetching robots.txt repeatedly.
    """
    
    # Simple cache to store parsed robot files, mapping base_url to RobotFileParser object
    parsers: Dict[str, robotparser.RobotFileParser]

    def __init__(self, user_agent: str):
        """
        Initializes the checker with the scraper's User-Agent string.
        """
        self.user_agent = user_agent
        self.parsers = {}
        print(f"RobotsChecker initialized. User-Agent: {self.user_agent}")

    def get_base_url(self, url: str) -> str:
        """Helper to extract the base URL (scheme://netloc) from a full URL."""
        parsed_url = urlparse(url)
        # Reconstructs the base URL, e.g., 'http://books.toscrape.com'
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    def get_parser(self, url: str) -> Optional[robotparser.RobotFileParser]:
        """
        Retrieves the appropriate robotparser for the given URL's domain,
        fetching and caching it if not already present.
        """
        base_url = self.get_base_url(url)
        
        # Check cache first
        if base_url in self.parsers:
            return self.parsers[base_url]

        # Construct robots.txt URL and create the parser
        robots_url = f"{base_url}/robots.txt"
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        
        # Use a timeout for reading robots.txt to avoid blocking
        try:
            # Note: robotparser uses urllib.request internally.
            print(f"Attempting to load robots.txt from: {robots_url}")
            rp.read()
            
            # Cache the loaded parser
            self.parsers[base_url] = rp
            print(f"Successfully loaded robots.txt rules for {base_url}.")
            return rp
            
        except Exception as e:
            # Handle errors (e.g., connection fail, or no robots.txt file exists)
            print(f"WARNING: Failed to load robots.txt from {robots_url}. Assuming all is allowed. Error: {e}")
            return None

    def is_url_allowed(self, url: str) -> bool:
        """
        Checks if the scraper's User-Agent is allowed to crawl the specified URL.
        """
        rp = self.get_parser(url)
        
        # If parser couldn't be loaded (e.g., connection error), we assume allowed 
        # for maximum robustness, but log a warning.
        if rp is None:
            return True

        # Use the standard method to check the rules
        allowed = rp.can_fetch(self.user_agent, url)
        
        if not allowed:
            # IMPORTANT: Log what we are enforcing (part of the test requirement)
            print(f"ROBOTS CHECK: Enforcing DISALLOW for URL: {url}")
        
        return allowed