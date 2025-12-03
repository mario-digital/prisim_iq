/**
 * Common schemas shared across the application.
 * Source: backend/src/schemas/data.py (ErrorResponse)
 */
import { z } from 'zod';

/**
 * Standard error response schema.
 * Source: backend/src/schemas/data.py::ErrorResponse
 */
export const ErrorResponseSchema = z.object({
  detail: z.string().describe('Error message'),
  error_code: z.string().nullable().optional().describe('Application error code'),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

