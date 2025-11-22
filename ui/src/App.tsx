import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { loadScrapedData } from './lib/loadData';
import { BookItem, FilterState, SortState, SortKey } from './types';
import Filters from './components/Filters';
import Table from './components/Table';
import Chart from './components/Chart';

// Initial states
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
    const [rawData, setRawData] = useState<BookItem[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const [filterState, setFilterState] = useState<FilterState>(INITIAL_FILTER_STATE);
    const [sortState, setSortState] = useState<SortState>(INITIAL_SORT_STATE);

    // --- NEW: pagination state ---
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 20;

    // Reset to page 1 whenever filter or sort changes
    useEffect(() => {
        setCurrentPage(1);
    }, [filterState, sortState]);

    // Load data
    useEffect(() => {
        loadScrapedData()
            .then(data => {
                setRawData(data);
                setIsLoading(false);
            })
            .catch(err => {
                console.error("Failed to load data:", err);
                setIsLoading(false);
            });
    }, []);

    // Handlers
    const handleFilterChange = useCallback((newFilters: FilterState) => {
        setFilterState(newFilters);
    }, []);

    const handleSortChange = useCallback((key: SortKey) => {
        setSortState(prev => {
            if (prev.key === key) {
                return {
                    key,
                    direction: prev.direction === "asc" ? "desc" : "asc",
                };
            }
            return { key, direction: "asc" };
        });
    }, []);

    // Available Categories
    const availableCategories = useMemo(() => {
        const cats = rawData.map(i => i.category);
        return ["All", ...Array.from(new Set(cats))].sort();
    }, [rawData]);

    // --- Filtering + Sorting logic (unchanged) ---
    const filteredAndSortedData = useMemo(() => {
        let result = rawData;
        const { searchTerm, minRating, categoryFilter } = filterState;

        // Filter
        result = result.filter(item => {
            if (item.rating < minRating) return false;
            if (categoryFilter !== "All" && item.category !== categoryFilter) return false;

            if (searchTerm) {
                const q = searchTerm.toLowerCase();
                const title = item.title.toLowerCase();
                const cat = item.category.toLowerCase();
                if (!title.includes(q) && !cat.includes(q)) return false;
            }

            return true;
        });

        // Sort
        if (sortState.key !== "none") {
            const { key, direction } = sortState;
            result = [...result].sort((a, b) => {
                const av = a[key];
                const bv = b[key];

                if (typeof av === "number" && typeof bv === "number") {
                    return direction === "asc" ? av - bv : bv - av;
                }
                if (typeof av === "string" && typeof bv === "string") {
                    return direction === "asc"
                        ? av.localeCompare(bv)
                        : bv.localeCompare(av);
                }
                return 0;
            });
        }

        return result;
    }, [rawData, filterState, sortState]);

    // --- NEW: Pagination computations ---
    const totalItems = filteredAndSortedData.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    const pagedData = useMemo(() => {
        const start = (currentPage - 1) * itemsPerPage;
        return filteredAndSortedData.slice(start, start + itemsPerPage);
    }, [filteredAndSortedData, currentPage]);

    // Loading & empty states unchanged
    if (isLoading) {
        return <div className="p-8 text-center text-lg font-medium text-indigo-600">Loading scraped data...</div>;
    }

    if (rawData.length === 0) {
        return <div className="p-8 text-center text-lg text-red-600 font-medium">
            No data found. Please run the scraper first.
        </div>;
    }

    return (
        <div className="container mx-auto p-4 md:p-8">
            <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Books Scraper Dashboard</h1>

            {/* Filters */}
            <Filters
                currentFilters={filterState}
                onFilterChange={handleFilterChange}
                availableCategories={availableCategories}
            />

            {/* Chart */}
            <Chart data={filteredAndSortedData} />

            {/* Count */}
            <div className="text-sm text-gray-600 my-4 text-center md:text-left">
                Displaying {pagedData.length} of {totalItems} filtered items.
            </div>

            {/* Table — now uses pagedData instead of filteredAndSortedData */}
            <Table
                data={pagedData}
                currentSort={sortState}
                onSortChange={handleSortChange}
            />

            {/* --- NEW PAGINATION UI --- */}
            <div className="flex justify-center items-center gap-4 mt-6">
                <button
                    className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                >
                    Previous
                </button>

                <span className="text-gray-700">
                    Page {currentPage} / {totalPages}
                </span>

                <button
                    className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                >
                    Next
                </button>
            </div>
        </div>
    );
};

export default App;
