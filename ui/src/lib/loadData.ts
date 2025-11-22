// ui/src/lib/loadData.ts

import { BookItem } from '../types';

// Assumes the file is in a publicly accessible path after build
const DATA_FILE_PATH = '/data/items.jsonl'; 

/**
 * Loads the JSONL data file, processes each line, and performs type coercion.
 * @returns A Promise that resolves to an array of BookItem objects.
 */
export async function loadScrapedData(): Promise<BookItem[]> {
    console.log(`Attempting to load data from: ${DATA_FILE_PATH}`);
    
    try {
        // 1. Fetch the raw content (a single string containing all JSON lines)
        const response = await fetch(DATA_FILE_PATH);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const rawJsonlText = await response.text();

        // 2. Split the content by newline to get individual JSON strings
        const lines = rawJsonlText.trim().split('\n');

        const items: BookItem[] = [];

        // 3. Process each line
        for (const line of lines) {
            if (!line) continue;

            try {
                // Parse the line into a raw JavaScript object
                const rawItem = JSON.parse(line);

                // 4. Perform Type Coercion and Structure Validation
                // This step ensures data types match our TypeScript interface
                const bookItem: BookItem = {
                    title: String(rawItem.title || 'N/A'),
                    // Ensure price is a number, not a string
                    price: parseFloat(rawItem.price) || 0,
                    availability: String(rawItem.availability || 'N/A'),
                    // Ensure rating is an integer
                    rating: parseInt(rawItem.rating, 10) || 0, 
                    category: String(rawItem.category || 'Unknown'),
                    url: String(rawItem.url || ''),
                    // Optional field
                    image_url: rawItem.image_url ? String(rawItem.image_url) : undefined,
                };
                
                items.push(bookItem);

            } catch (parseError) {
                console.error("Error parsing JSON line:", line, parseError);
                // Continue to the next line if one line is corrupted
            }
        }
        
        console.log(`Successfully loaded ${items.length} unique book items.`);
        return items;

    } catch (error) {
        console.error("Failed to load data file:", error);
        // Return an empty array on failure
        return []; 
    }
}