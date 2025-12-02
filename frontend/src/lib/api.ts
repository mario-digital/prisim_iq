/**
 * API Configuration Utility
 * Centralizes API endpoint configuration and URL building
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiConfig = {
  baseUrl: API_BASE_URL,
  endpoints: {
    health: '/health',
    segments: '/api/segments',
    optimize: '/api/optimize-price',
    explain: '/api/explain-decision',
    sensitivity: '/api/sensitivity-analysis',
    evidence: '/api/evidence',
  },
} as const;

/**
 * Build a full API URL from a path
 * @param path - The API path (with or without leading slash)
 * @returns Full API URL
 */
export function apiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

export type ApiEndpoint = keyof typeof apiConfig.endpoints;

