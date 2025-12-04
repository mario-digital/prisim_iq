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

/**
 * Information about a single ML model.
 * Source: backend/src/schemas/health.py::ModelInfo
 */
export const ModelInfoSchema = z.object({
  name: z.string().describe('Model name/identifier'),
  loaded: z.boolean().describe('Whether the model is loaded in memory'),
  type: z.string().describe('Model type (e.g., xgboost, linear_regression)'),
});

/**
 * Response model for models status endpoint.
 * Source: backend/src/schemas/health.py::ModelsStatusResponse
 */
export const ModelsStatusResponseSchema = z.object({
  total: z.number().int().describe('Total number of models'),
  ready: z.number().int().describe('Number of models loaded and ready'),
  models: z.array(ModelInfoSchema).describe('Details for each model'),
  timestamp: z.string().datetime().describe('Current server timestamp (UTC)'),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type HealthStatusType = z.infer<typeof HealthStatus>;
export type ModelInfo = z.infer<typeof ModelInfoSchema>;
export type ModelsStatusResponse = z.infer<typeof ModelsStatusResponseSchema>;

