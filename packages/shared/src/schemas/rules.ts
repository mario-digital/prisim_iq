/**
 * Business rules schemas for price adjustments.
 * Source: backend/src/rules/engine.py
 */
import { z } from 'zod';

/**
 * Record of a single rule application.
 * Source: backend/src/rules/engine.py::AppliedRule
 */
export const AppliedRuleSchema = z.object({
  rule_id: z.string().describe('Unique rule identifier'),
  rule_name: z.string().describe('Human-readable rule name'),
  price_before: z.number().describe('Price before rule application'),
  price_after: z.number().describe('Price after rule application'),
  impact: z.number().describe('Absolute price change'),
  impact_percent: z.number().describe('Percentage price change'),
});

export type AppliedRule = z.infer<typeof AppliedRuleSchema>;

/**
 * Result of applying all business rules.
 * Source: backend/src/rules/engine.py::RulesResult
 */
export const RulesResultSchema = z.object({
  original_price: z.number().describe('Price before any rules'),
  final_price: z.number().describe('Price after all rules applied'),
  applied_rules: z.array(AppliedRuleSchema).default([]).describe('List of rules that were applied'),
  total_adjustment: z.number().describe('Total price adjustment'),
  total_adjustment_percent: z.number().describe('Total adjustment as percentage'),
});

export type RulesResult = z.infer<typeof RulesResultSchema>;

