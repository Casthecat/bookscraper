from dataclasses import dataclass
from typing import Optional, Dict, Any, NamedTuple

SCHEMA_VERSION = 1 


@dataclass(frozen=True)
class BookItem:
    """
    Defines the structure for a single scraped book product.
    Fields correspond to the required deliverables in the test document.
    """
    title: str
    price: float
    availability: str
    rating: int
    category: str
    url: str
    image_url: Optional[str] = None

    def to_jsonl(self) -> Dict[str, Any]:
        """
        Converts the dataclass instance to a dictionary for JSONL output.
        We can remove optional fields if they are None here for clean output.
        """
        # Exclude None values for clean JSON output
        data = {k: v for k, v in self.__dict__.items() if v is not None}
        data["schema_version"] = SCHEMA_VERSION 
        return data


class ScraperArgs(NamedTuple):
    """
    A structure to hold and pass command-line arguments.
    """
    start: str
    max_pages: int
    delay_ms: int
    dry_run: bool
    concurrency: int
