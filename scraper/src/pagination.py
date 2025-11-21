from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse
import os 

def get_base_url(url: str) -> str:
    """Helper to extract the base URL (scheme://netloc) from a full URL."""
    parsed_url = urlparse(url)
    # Reconstructs the base URL, e.g., 'http://books.toscrape.com'
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def get_next_page_url(html_content: str, current_url: str) -> Optional[str]:
    """
    Finds the 'Next Page' link from the HTML content and returns the absolute URL.
    
    This function uses directory-aware resolution to correctly handle relative links 
    on both index pages and deep category pages, fixing 404 issues.
    
    Args:
        html_content: The HTML content of the current page.
        current_url: The URL of the current page (needed for resolving relative links).
        
    Returns:
        The absolute URL of the next page, or None if no next link is found.
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Use the specific CSS selector for the 'Next' button
    next_link_tag = soup.select_one('li.next a')
    
    if next_link_tag:
        # Extract the relative URL
        relative_url = next_link_tag.get('href')
        
        if relative_url:
            
            # --- CRITICAL FIX FOR 404 ERRORS ---
            parsed = urlparse(current_url)
            
            # 1. Use os.path.dirname to intelligently strip the filename and get the directory path.
            # Example: '/catalogue/category/fiction_10/index.html' -> '/catalogue/category/fiction_10'
            # The rstrip('/') is necessary to handle cases where the path might end with a slash.
            base_path = os.path.dirname(parsed.path.rstrip('/'))
            
            # 2. Reconstruct the directory path, ensuring it ends with a '/' for correct joining.
            if base_path:
                # Append '/' to the directory path
                directory_path = base_path + '/'
            else:
                # If path is empty (e.g., domain root), use '/'
                directory_path = '/'
            
            # 3. Reconstruct the base URL structure using the determined directory path
            base_for_join = urlunparse((
                parsed.scheme,
                parsed.netloc,
                directory_path, 
                parsed.params,
                parsed.query,
                '' # Anchor fragment is empty
            ))
            
            # 4. Join the directory base with the relative URL
            absolute_url = urljoin(base_for_join, relative_url)
            
            print(f"Pagination found: Next page resolved from '{directory_path}' to {absolute_url}")
            return absolute_url
        
    # If no link is found, we are on the last page
    print("Pagination end: No further 'Next Page' link found.")
    return None

def get_base_url(url: str) -> str:
    """Helper to extract the base URL (scheme://netloc) from a full URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"