import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { loadScrapedData } from './lib/loadData'; // Removed .ts extension for better compatibility
import { BookItem, FilterState, SortState, SortKey } from './types';
import Filters from './components/Filters'; // Removed .tsx extension
import Table from './components/Table';     // Removed .tsx extension
import Chart from './components/Chart';     // Removed .tsx extension

// Define initial states
const INITIAL_FILTER_STATE: FilterState = {
    searchTerm: '',
    minRating: 0,
    categoryFilter: 'All',
};

const INITIAL_SORT_STATE: SortState = {
    key: 'none',
    direction: 'asc',
};

const App: React.FC = () => {
    //  Data States
    const [rawData, setRawData] = useState<BookItem[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    //  Control States
    const [filterState, setFilterState] = useState<FilterState>(INITIAL_FILTER_STATE);
    const [sortState, setSortState] = useState<SortState>(INITIAL_SORT_STATE);

    // --- Data Loading Effect ---
    useEffect(() => {
        // Load data on component mount
        loadScrapedData()
            .then(data => {
                setRawData(data);
                setIsLoading(false);
            })
            .catch(error => {
                console.error("Failed to load initial data:", error);
                setIsLoading(false);
            });
    }, []);

    // --- Handlers (Passed to child components) ---

    // Handler for updating filter state from the Filters component
    const handleFilterChange = useCallback((newFilters: FilterState) => {
        setFilterState(newFilters);
    }, []);

    // Handler for updating sort state from the Table component
    const handleSortChange = useCallback((key: SortKey) => {
        setSortState(prevSort => {
            // If clicking the currently sorted column, toggle direction
            if (prevSort.key === key) {
                return {
                    key,
                    direction: prevSort.direction === 'asc' ? 'desc' : 'asc',
                };
            }
            // Otherwise, set new column to ascending
            return {
                key,
                direction: 'asc',
            };
        });
    }, []);
    
    // Calculate list of unique categories for the filter component
    const availableCategories = useMemo(() => {
        const categories = rawData.map(item => item.category);
        // Include 'All' option and sort the categories
        return ['All', ...Array.from(new Set(categories))].sort();
    }, [rawData]);


    // --- Core Data Processing Logic (Filtering and Sorting) ---
    const filteredAndSortedData = useMemo(() => {
        let result = rawData;
        const { searchTerm, minRating, categoryFilter } = filterState;
        const { key: sortKey, direction: sortDirection } = sortState;

        // Filtering Logic
        result = result.filter(item => {
            // Rating Filter
            if (item.rating < minRating) {
                return false;
            }
            
            // Category Filter
            if (categoryFilter !== 'All' && item.category !== categoryFilter) {
                return false;
            }

            // Search Term Filter (Case-insensitive check in title and category)
            if (searchTerm) {
                const term = searchTerm.toLowerCase();
                if (
                    !item.title.toLowerCase().includes(term) &&
                    !item.category.toLowerCase().includes(term)
                ) {
                    return false;
                }
            }
            
            return true;
        });


        //  Sorting Logic
        if (sortKey !== 'none') {
            result.sort((a, b) => {
                const aValue = a[sortKey];
                const bValue = b[sortKey];
                
                // Handling numbers (Price, Rating)
                if (typeof aValue === 'number' && typeof bValue === 'number') {
                    if (sortDirection === 'asc') return aValue - bValue;
                    return bValue - aValue;
                }
                
                // Handling strings (case-insensitive comparison, e.g., Title, Category)
                if (typeof aValue === 'string' && typeof bValue === 'string') {
                    const comparison = aValue.toLowerCase().localeCompare(bValue.toLowerCase());
                    return sortDirection === 'asc' ? comparison : -comparison;
                }
                
                return 0;
            });
        }
        
        return result;
        
    }, [rawData, filterState, sortState]); // Dependencies: Recalculate only when necessary


    if (isLoading) {
        return <div className="p-8 text-center text-lg font-medium text-indigo-600">Loading scraped data...</div>;
    }

    if (rawData.length === 0) {
         return <div className="p-8 text-center text-lg text-red-600 font-medium">
             Failed to load data or the items.jsonl file is empty. Please run the scraper first.
         </div>;
    }

    return (
        <div className="container mx-auto p-4 md:p-8">
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Books Scraper Dashboard</h1>

            {/* Filters Component */}
            <Filters 
                currentFilters={filterState}
                onFilterChange={handleFilterChange}
                availableCategories={availableCategories}
            />
            
            {/* Chart Component */}
            <Chart 
                data={filteredAndSortedData}
            />

            {/* Displaying Results Count */}
            <div className="text-sm text-gray-600 my-4 text-center md:text-left">
                Displaying {filteredAndSortedData.length} of {rawData.length} total items.
            </div>

            {/* Table Component */}
            <Table 
                data={filteredAndSortedData}
                currentSort={sortState}
                onSortChange={handleSortChange}
            />
        </div>
    );
};

export default App;