// ui/src/types.ts

// Corresponds to the BookItem structure defined in the Python Scraper
export interface BookItem {
    title: string;
    price: number;
    availability: string;
    rating: number; // 1 to 5 stars
    category: string;
    url: string;
    image_url?: string; // Optional field
}

// Defines the application's filtering state
export interface FilterState {
    searchTerm: string; // Search keyword (Title/Category)
    minRating: number;  // Minimum rating (e.g., 3 stars and above)
    categoryFilter: string; // Category filter (e.g., "Travel")
}

// Defines the available keys for sorting
export type SortKey = keyof BookItem | 'none'; // Allow sorting by any BookItem key or no sort
export type SortDirection = 'asc' | 'desc';

// Defines the application's sorting state
export interface SortState {
    key: SortKey;
    direction: SortDirection;
}