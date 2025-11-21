// ui/src/components/Table.tsx

import React from 'react';
import { BookItem, SortState, SortKey, SortDirection } from '../types';


interface TableProps {
    data: BookItem[];
    currentSort: SortState;
    onSortChange: (key: SortKey) => void;
}

// Define the headers based on the BookItem keys
interface TableHeader {
    key: SortKey; // Must match the key in BookItem or 'none'
    label: string;
    isSortable: boolean;
    className?: string; // For styling (using Tailwind CSS utilities)
}

// Table column configuration
const HEADERS: TableHeader[] = [
    { key: 'title', label: 'Title', isSortable: true, className: "w-1/3 text-left" },
    { key: 'category', label: 'Category', isSortable: true, className: "w-1/6 hidden md:table-cell text-left" },
    { key: 'rating', label: 'Rating', isSortable: true, className: "w-[80px] text-center" },
    { key: 'price', label: 'Price (GBP)', isSortable: true, className: "w-[120px] text-right" },
    { key: 'availability', label: 'Availability', isSortable: false, className: "w-1/6 hidden sm:table-cell text-left" },
    { key: 'url', label: 'Link', isSortable: false, className: "w-[80px] text-center hidden lg:table-cell" },
];

// Helper function to render star icons
const renderRatingStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
        <span 
            key={index} 
            className={`text-xl ${index < rating ? 'text-yellow-400' : 'text-gray-300'}`}
        >
            ★
        </span>
    ));
};

// Helper function to display sort arrow
const renderSortArrow = (key: SortKey, currentSort: SortState) => {
    if (currentSort.key !== key) return null;
    
    if (currentSort.direction === 'asc') {
        return <span className="ml-1">▲</span>; // Up arrow (Ascending)
    }
    return <span className="ml-1">▼</span>; // Down arrow (Descending)
};


const Table: React.FC<TableProps> = ({ data, currentSort, onSortChange }) => {
    
    if (data.length === 0) {
        return (
            <div className="text-center p-10 bg-white rounded-lg shadow-md">
                No books match the current filters.
            </div>
        );
    }
    
    return (
        <div className="overflow-x-auto bg-white rounded-lg shadow-xl">
            <table className="min-w-full divide-y divide-gray-200">
                
                {/* Table Header */}
                <thead className="bg-gray-50 sticky top-0 z-10">
                    <tr>
                        {HEADERS.map(header => (
                            <th
                                key={header.key}
                                className={`px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${header.className || ''} ${header.isSortable ? 'cursor-pointer hover:bg-gray-200 transition duration-150' : ''}`}
                                onClick={() => header.isSortable && onSortChange(header.key)}
                            >
                                <div className="flex items-center justify-center">
                                    {header.label}
                                    {header.isSortable && renderSortArrow(header.key, currentSort)}
                                </div>
                            </th>
                        ))}
                    </tr>
                </thead>
                
                {/* Table Body */}
                <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((item, index) => (
                        <tr 
                            key={index} 
                            className="hover:bg-blue-50 transition duration-150"
                        >
                            {/* Title (Clickable) */}
                            <td className="px-4 py-3 whitespace-normal text-sm font-medium text-gray-900">
                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 hover:underline">
                                    {item.title}
                                </a>
                            </td>

                            {/* Category */}
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                                {item.category}
                            </td>
                            
                            {/* Rating */}
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                                {renderRatingStars(item.rating)}
                            </td>

                            {/* Price */}
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-green-700">
                                £{item.price.toFixed(2)}
                            </td>

                            {/* Availability */}
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                                {item.availability}
                            </td>
                            
                            {/* URL Link */}
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-center hidden lg:table-cell">
                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-600">
                                    View Page
                                </a>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Table;