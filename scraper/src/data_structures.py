from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, NamedTuple

@dataclass(frozen=True) 
class BookItem:
    """
    Defines the structure for a single scraped book product.
    Fields correspond to the required deliverables in the test document.
    """
    title: str
    price: float
    availability: str
    rating: int          # 1 to 5 stars
    category: str
    url: str             # Product page URL (relative or absolute
    image_url: Optional[str] = None    # For extensibility or debugging
    
    def to_jsonl(self) -> Dict[str, Any]:
        """
        Converts the dataclass instance to a dictionary for JSONL output.
        We can remove optional fields if they are None here for clean output.
        """
        # Exclude None values for clean JSON output
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
class ScraperArgs(NamedTuple):
    """
    A structure to hold and pass command-line arguments.
    """
    start: str
    max_pages: int
    delay_ms: int
    dry_run: bool