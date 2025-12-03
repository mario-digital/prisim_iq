/**
 * Decision trace schemas for auditing pricing pipeline decisions.
 * Source: backend/src/explainability/decision_trace.py
 */
import { z } from 'zod';

export const TraceStepStatus = z.enum(['success', 'error', 'skipped']);
export const AgreementStatus = z.enum(['full_agreement', 'partial_agreement', 'divergent']);

/**
 * A single step in the decision trace.
 * Source: backend/src/explainability/decision_trace.py::TraceStep
 */
export const TraceStepSchema = z.object({
  step_name: z.string().describe('Pipeline step identifier'),
  timestamp: z.string().datetime().describe('Step start timestamp'),
  duration_ms: z.number().min(0).describe('Step duration in milliseconds'),
  inputs: z.record(z.string(), z.unknown()).default({}).describe('Step inputs'),
  outputs: z.record(z.string(), z.unknown()).default({}).describe('Step outputs'),
  status: TraceStepStatus.describe('Step completion status'),
  error_message: z.string().nullable().optional().describe('Error message if failed'),
});

export type TraceStep = z.infer<typeof TraceStepSchema>;

/**
 * Model agreement analysis across all prediction models.
 * Source: backend/src/explainability/decision_trace.py::ModelAgreement
 */
export const ModelAgreementSchema = z.object({
  models_compared: z.array(z.string()).describe('Models used in comparison'),
  predictions: z.record(z.string(), z.number()).describe('Model predictions mapping'),
  max_deviation_percent: z.number().min(0).describe('Maximum deviation percentage'),
  is_agreement: z.boolean().describe('Whether models agree within 10%'),
  status: AgreementStatus.describe('Agreement status classification'),
});

export type ModelAgreement = z.infer<typeof ModelAgreementSchema>;

/**
 * Complete decision trace for a pricing request.
 * Source: backend/src/explainability/decision_trace.py::DecisionTrace
 */
export const DecisionTraceSchema = z.object({
  trace_id: z.string().describe('Unique trace identifier'),
  request_timestamp: z.string().datetime().describe('Request start timestamp'),
  total_duration_ms: z.number().min(0).describe('Total execution time in ms'),
  steps: z.array(TraceStepSchema).default([]).describe('Pipeline steps'),
  model_agreement: ModelAgreementSchema.nullable().optional().describe('Model agreement analysis'),
  final_result: z.record(z.string(), z.unknown()).default({}).describe('Final pricing result'),
});

export type DecisionTrace = z.infer<typeof DecisionTraceSchema>;
export type TraceStepStatusType = z.infer<typeof TraceStepStatus>;
export type AgreementStatusType = z.infer<typeof AgreementStatus>;

