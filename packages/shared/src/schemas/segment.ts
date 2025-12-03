/**
 * Segment result schemas for classification output.
 * Source: backend/src/schemas/segment.py
 */
import { z } from 'zod';

export const ConfidenceLevel = z.enum(['high', 'medium', 'low']);

/**
 * Basic result of market context classification into a segment.
 * Source: backend/src/schemas/segment.py::SegmentResult
 */
export const SegmentResultSchema = z.object({
  segment_name: z
    .string()
    .describe("Descriptive name of the segment (e.g., 'Urban_Peak_Premium')"),
  cluster_id: z.number().int().min(0).describe('Numeric cluster ID from K-Means'),
  characteristics: z
    .record(z.string(), z.unknown())
    .default({})
    .describe('Key characteristics of this segment (e.g., avg_surge, avg_demand_ratio)'),
  centroid_distance: z
    .number()
    .min(0)
    .describe('Distance from cluster centroid (lower = higher confidence)'),
});

export type SegmentResult = z.infer<typeof SegmentResultSchema>;

/**
 * Full segment classification response for API output.
 * Source: backend/src/schemas/segment.py::SegmentDetails
 */
export const SegmentDetailsSchema = z.object({
  segment_name: z
    .string()
    .describe("Descriptive name of the segment (e.g., 'Urban_Peak_Premium')"),
  cluster_id: z.number().int().min(0).describe('Numeric cluster ID from K-Means'),
  characteristics: z
    .record(z.string(), z.unknown())
    .default({})
    .describe(
      'Key characteristics of this segment (e.g., avg_supply_demand_ratio, sample_count)'
    ),
  centroid_distance: z
    .number()
    .min(0)
    .describe('Distance from cluster centroid (lower = more confident)'),
  human_readable_description: z.string().describe('Human-friendly explanation of the segment'),
  confidence_level: ConfidenceLevel.describe('Confidence level based on centroid distance'),
});

export type SegmentDetails = z.infer<typeof SegmentDetailsSchema>;
export type ConfidenceLevelType = z.infer<typeof ConfidenceLevel>;

