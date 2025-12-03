/**
 * @prismiq/shared - Shared types, schemas, and constants for PrismIQ
 *
 * Usage:
 *   // For types only (no runtime validation)
 *   import type { MarketContext } from '@prismiq/shared';
 *
 *   // For schemas with runtime validation
 *   import { MarketContextSchema, type MarketContext } from '@prismiq/shared/schemas';
 *
 *   // For constants
 *   import { API_ENDPOINTS } from '@prismiq/shared/constants';
 */

// Types (re-exported from schemas for convenience)
export * from './types';

// Constants
export * from './constants';

// Note: Schemas are available at '@prismiq/shared/schemas'
// Import from there for Zod schema objects with runtime validation

