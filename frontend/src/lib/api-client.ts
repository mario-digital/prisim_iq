/**
 * Validated API Client
 *
 * Provides type-safe API calls with runtime validation using Zod schemas.
 * All responses are validated against their corresponding schemas to ensure
 * API contract compliance and catch drift early.
 */
import ky, { type Options } from 'ky';
import { type ZodError, type ZodType } from 'zod';
import { API_BASE_URL } from './api';

/**
 * Custom error class for validation failures.
 * Contains the original Zod error with detailed issue information.
 */
export class ValidationError extends Error {
  public readonly endpoint: string;
  public readonly zodError: ZodError;
  public readonly issues: Array<{
    path: PropertyKey[];
    message: string;
    code: string;
  }>;

  constructor(endpoint: string, zodError: ZodError) {
    const issueMessages = zodError.issues.map(
      (issue) => `${String(issue.path.join('.'))}: ${issue.message}`
    );
    super(`API response validation failed for ${endpoint}: ${issueMessages.join('; ')}`);

    this.name = 'ValidationError';
    this.endpoint = endpoint;
    this.zodError = zodError;
    this.issues = zodError.issues.map((issue) => ({
      path: issue.path,
      message: issue.message,
      code: issue.code,
    }));
  }
}

/**
 * Configured ky instance with base URL and default options.
 */
const api = ky.create({
  prefixUrl: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch data from an endpoint and validate the response against a Zod schema.
 *
 * @param endpoint - API endpoint path (without base URL)
 * @param schema - Zod schema to validate the response
 * @param options - Optional ky request options
 * @returns Validated and typed response data
 * @throws ValidationError if response doesn't match schema
 * @throws HTTPError if request fails
 *
 * @example
 * ```ts
 * import { HealthResponseSchema } from '@prismiq/shared/schemas';
 *
 * const health = await fetchValidated('health', HealthResponseSchema);
 * // health is typed as HealthResponse
 * ```
 */
export async function fetchValidated<T>(
  endpoint: string,
  schema: ZodType<T>,
  options?: Options
): Promise<T> {
  const response = await api.get(endpoint, options).json();

  const result = schema.safeParse(response);

  if (!result.success) {
    console.error('API Response Validation Failed:', {
      endpoint,
      issues: result.error.issues,
      response,
    });
    throw new ValidationError(endpoint, result.error);
  }

  return result.data;
}

/**
 * Post data to an endpoint and validate the response against a Zod schema.
 *
 * @param endpoint - API endpoint path (without base URL)
 * @param schema - Zod schema to validate the response
 * @param body - Request body (will be JSON serialized)
 * @param options - Optional ky request options
 * @returns Validated and typed response data
 * @throws ValidationError if response doesn't match schema
 * @throws HTTPError if request fails
 *
 * @example
 * ```ts
 * import { PricingResultSchema, type MarketContext } from '@prismiq/shared/schemas';
 *
 * const context: MarketContext = { ... };
 * const result = await postValidated('api/optimize-price', PricingResultSchema, context);
 * // result is typed as PricingResult
 * ```
 */
export async function postValidated<T, B = unknown>(
  endpoint: string,
  schema: ZodType<T>,
  body: B,
  options?: Options
): Promise<T> {
  const response = await api
    .post(endpoint, {
      json: body,
      ...options,
    })
    .json();

  const result = schema.safeParse(response);

  if (!result.success) {
    console.error('API Response Validation Failed:', {
      endpoint,
      issues: result.error.issues,
      response,
    });
    throw new ValidationError(endpoint, result.error);
  }

  return result.data;
}

/**
 * Fetch data without validation (for endpoints without schemas or streaming).
 * Use sparingly - prefer fetchValidated when possible.
 */
export async function fetchRaw<T = unknown>(endpoint: string, options?: Options): Promise<T> {
  return api.get(endpoint, options).json<T>();
}

/**
 * Post data without validation (for endpoints without schemas or streaming).
 * Use sparingly - prefer postValidated when possible.
 */
export async function postRaw<T = unknown, B = unknown>(
  endpoint: string,
  body: B,
  options?: Options
): Promise<T> {
  return api.post(endpoint, { json: body, ...options }).json<T>();
}

/**
 * Get the configured ky instance for advanced use cases (streaming, etc.).
 */
export { api };

