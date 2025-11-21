// ui/src/components/Chart.tsx

import React, { useMemo } from 'react';
import { BookItem } from '../types';

interface ChartProps {
    data: BookItem[]; // Filtered data passed from App.tsx
}

interface ChartData {
    rating: number; // 1 to 5
    count: number;
}

const Chart: React.FC<ChartProps> = ({ data }) => {
    
    // Core logic: Aggregate data by rating
    const ratingData: ChartData[] = useMemo(() => {
        // 1. Initialize count map for ratings 1 through 5
        const counts = new Map<number, number>();
        for (let i = 1; i <= 5; i++) {
            counts.set(i, 0);
        }

        // 2. Iterate over all books and count ratings
        data.forEach(item => {
            if (item.rating >= 1 && item.rating <= 5) {
                counts.set(item.rating, counts.get(item.rating)! + 1);
            }
        });

        // 3. Convert map to array for rendering, sorting by rating descending
        return Array.from(counts.entries())
            .map(([rating, count]) => ({ rating, count }))
            .sort((a, b) => b.rating - a.rating); // 5 stars first
            
    }, [data]); // Recalculate whenever the input data changes

    // Find the maximum count to normalize bar heights
    const maxCount = Math.max(...ratingData.map(d => d.count), 1); // Max must be at least 1

    return (
        <div className="chart-container p-6 bg-white rounded-lg shadow-xl mt-6">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Book Count by Rating (1-5 Stars)</h2>
            
            <div className="flex flex-col space-y-3">
                {ratingData.map(({ rating, count }) => {
                    // Calculate bar width as a percentage of the max count
                    const widthPercent = (count / maxCount) * 100;
                    
                    return (
                        <div key={rating} className="flex items-center">
                            {/* Label */}
                            <div className="w-16 font-semibold text-gray-600 text-right pr-3 flex-shrink-0">
                                {rating} ★
                            </div>
                            
                            {/* Bar */}
                            <div className="flex-grow bg-gray-200 h-6 rounded-md overflow-hidden">
                                <div
                                    style={{ width: `${widthPercent}%` }}
                                    className={`h-full transition-all duration-500 ease-out 
                                        ${count > 0 ? 'bg-indigo-500' : 'bg-transparent'}`
                                    }
                                >
                                    {/* Text inside the bar */}
                                    <span className="pl-2 text-sm text-white font-medium flex items-center h-full">
                                        {count > 0 ? count : ''}
                                    </span>
                                </div>
                            </div>

                            {/* Count (outside the bar for 0 counts) */}
                            {count === 0 && <span className="ml-3 text-sm text-gray-500">{count}</span>}
                        </div>
                    );
                })}
            </div>
            {/* Legend/Note */}
            <p className="text-xs text-gray-500 mt-4">
                Visualization based on the currently filtered {data.length} items.
            </p>
        </div>
    );
};

export default Chart;