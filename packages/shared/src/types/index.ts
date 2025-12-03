/**
 * Shared TypeScript types for PrismIQ.
 *
 * IMPORTANT: Two type systems coexist:
 *
 * 1. LEGACY TYPES (this file) - camelCase, frontend-specific
 *    - Used by existing frontend components
 *    - Import from '@prismiq/shared' or '@prismiq/shared/types'
 *
 * 2. ZOD SCHEMAS (schemas/) - snake_case, matches backend Pydantic
 *    - Used for API validation and runtime type safety
 *    - Import from '@prismiq/shared/schemas'
 *
 * The API client layer handles transformation between the two.
 */

// Legacy frontend types (camelCase, frontend-specific)
export * from './market';
export * from './pricing';
export * from './chat';
export * from './scenario';

// Note: For API-validated types matching backend, use '@prismiq/shared/schemas'
