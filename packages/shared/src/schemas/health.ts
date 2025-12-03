/**
 * Health check response schemas.
 * Source: backend/src/schemas/health.py
 */
import { z } from 'zod';

export const HealthStatus = z.enum(['healthy', 'degraded', 'unhealthy']);

/**
 * Response model for health check endpoint.
 * Source: backend/src/schemas/health.py::HealthResponse
 */
export const HealthResponseSchema = z.object({
  status: HealthStatus.describe('Current health status of the API'),
  version: z.string().describe('API version string'),
  timestamp: z.string().datetime().describe('Current server timestamp (UTC)'),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type HealthStatusType = z.infer<typeof HealthStatus>;

