// ui/src/components/Filters.tsx

import React from 'react';
import { FilterState } from '../types';

interface FiltersProps {
    currentFilters: FilterState;
    onFilterChange: (newFilters: FilterState) => void;
    availableCategories: string[]; // List of unique categories from App.tsx
}

const ratingOptions = [
    { label: 'All Ratings', value: 0 },
    { label: '1 Star & Up', value: 1 },
    { label: '2 Stars & Up', value: 2 },
    { label: '3 Stars & Up', value: 3 },
    { label: '4 Stars & Up', value: 4 },
    { label: '5 Stars Only', value: 5 },
];

const Filters: React.FC<FiltersProps> = ({ currentFilters, onFilterChange, availableCategories }) => {
    
    // Handler for text input change (Search)
    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        onFilterChange({
            ...currentFilters,
            searchTerm: event.target.value,
        });
    };

    // Handler for select input change (Rating or Category)
    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = event.target;
        
        if (name === 'minRating') {
            onFilterChange({
                ...currentFilters,
                minRating: parseInt(value, 10), // Convert string to number
            });
        } else if (name === 'categoryFilter') {
            onFilterChange({
                ...currentFilters,
                categoryFilter: value,
            });
        }
    };
    
    // Simple styling (using Tailwind CSS utility classes for demonstration)
    const inputStyle = "p-2 border border-gray-300 rounded-md w-full";
    const labelStyle = "block text-sm font-medium text-gray-700 mb-1";

    return (
        <div className="filters-container p-4 bg-gray-50 rounded-lg shadow-md mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* 1. Search Box */}
            <div>
                <label htmlFor="searchTerm" className={labelStyle}>Search (Title/Category)</label>
                <input
                    id="searchTerm"
                    type="text"
                    className={inputStyle}
                    placeholder="e.g., travel, fiction, Light"
                    value={currentFilters.searchTerm}
                    onChange={handleSearchChange}
                />
            </div>

            {/* 2. Category Filter */}
            <div>
                <label htmlFor="categoryFilter" className={labelStyle}>Filter by Category</label>
                <select
                    id="categoryFilter"
                    name="categoryFilter"
                    className={inputStyle}
                    value={currentFilters.categoryFilter}
                    onChange={handleSelectChange}
                >
                    {availableCategories.map(category => (
                        <option key={category} value={category}>
                            {category}
                        </option>
                    ))}
                </select>
            </div>

            {/* 3. Minimum Rating Filter */}
            <div>
                <label htmlFor="minRating" className={labelStyle}>Minimum Rating</label>
                <select
                    id="minRating"
                    name="minRating"
                    className={inputStyle}
                    value={currentFilters.minRating}
                    onChange={handleSelectChange}
                >
                    {ratingOptions.map(option => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
};

export default Filters;