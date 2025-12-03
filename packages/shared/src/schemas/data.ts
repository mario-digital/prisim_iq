/**
 * Data-related response schemas.
 * Source: backend/src/schemas/data.py
 */
import { z } from 'zod';

/**
 * Price range statistics.
 * Source: backend/src/schemas/data.py::PriceRange
 */
export const PriceRangeSchema = z.object({
  min: z.number().describe('Minimum price in dataset'),
  max: z.number().describe('Maximum price in dataset'),
});

export type PriceRange = z.infer<typeof PriceRangeSchema>;

/**
 * Response model for dataset summary endpoint.
 * Source: backend/src/schemas/data.py::DataSummaryResponse
 */
export const DataSummaryResponseSchema = z.object({
  row_count: z.number().int().describe('Total number of rows in the dataset'),
  column_count: z.number().int().describe('Total number of columns in the dataset'),
  segments: z.array(z.string()).describe('List of customer loyalty segments'),
  price_range: PriceRangeSchema.describe('Min/max price range'),
});

export type DataSummaryResponse = z.infer<typeof DataSummaryResponseSchema>;

