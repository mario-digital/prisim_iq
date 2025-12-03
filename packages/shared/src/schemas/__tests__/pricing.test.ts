import { describe, it, expect } from 'bun:test';
import { PricingResultSchema } from '../pricing';
import { AppliedRuleSchema, RulesResultSchema } from '../rules';
import { PriceDemandPointSchema, OptimizationResultSchema } from '../optimization';
import { SegmentDetailsSchema } from '../segment';

describe('PriceDemandPointSchema', () => {
    it('validates correct input', () => {
        const point = { price: 30.0, demand: 0.95, profit: 12.5 };
        expect(() => PriceDemandPointSchema.parse(point)).not.toThrow();
    });

    it('rejects demand > 1', () => {
        const point = { price: 30.0, demand: 1.5, profit: 12.5 };
        expect(() => PriceDemandPointSchema.parse(point)).toThrow();
    });

    it('rejects demand < 0', () => {
        const point = { price: 30.0, demand: -0.1, profit: 12.5 };
        expect(() => PriceDemandPointSchema.parse(point)).toThrow();
    });
});

describe('AppliedRuleSchema', () => {
    it('validates correct input', () => {
        const rule = {
            rule_id: 'floor_minimum_margin',
            rule_name: 'Minimum Margin Floor',
            price_before: 38.5,
            price_after: 42.5,
            impact: 4.0,
            impact_percent: 10.39,
        };
        const result = AppliedRuleSchema.safeParse(rule);
        expect(result.success).toBe(true);
    });
});

describe('RulesResultSchema', () => {
    it('validates correct input', () => {
        const result = {
            original_price: 38.5,
            final_price: 42.5,
            applied_rules: [],
            total_adjustment: 4.0,
            total_adjustment_percent: 10.39,
        };
        expect(() => RulesResultSchema.parse(result)).not.toThrow();
    });

    it('defaults applied_rules to empty array', () => {
        const result = {
            original_price: 38.5,
            final_price: 42.5,
            total_adjustment: 4.0,
            total_adjustment_percent: 10.39,
        };
        const parsed = RulesResultSchema.parse(result);
        expect(parsed.applied_rules).toEqual([]);
    });
});

describe('OptimizationResultSchema', () => {
    it('validates correct input', () => {
        const result = {
            optimal_price: 42.5,
            expected_demand: 0.72,
            expected_profit: 15.3,
            baseline_price: 35.0,
            baseline_profit: 10.5,
            profit_uplift_percent: 45.71,
            price_demand_curve: [
                { price: 30.0, demand: 0.95, profit: 0.0 },
                { price: 40.0, demand: 0.75, profit: 7.5 },
            ],
            optimization_time_ms: 245.5,
        };
        expect(() => OptimizationResultSchema.parse(result)).not.toThrow();
    });

    it('rejects negative optimization_time_ms', () => {
        const result = {
            optimal_price: 42.5,
            expected_demand: 0.72,
            expected_profit: 15.3,
            baseline_price: 35.0,
            baseline_profit: 10.5,
            profit_uplift_percent: 45.71,
            price_demand_curve: [],
            optimization_time_ms: -10,
        };
        expect(() => OptimizationResultSchema.parse(result)).toThrow();
    });
});

describe('SegmentDetailsSchema', () => {
    it('validates correct input', () => {
        const segment = {
            segment_name: 'Urban_Peak_Premium',
            cluster_id: 2,
            characteristics: { avg_supply_demand_ratio: 0.65 },
            centroid_distance: 0.45,
            human_readable_description: 'High-demand urban area',
            confidence_level: 'high',
        };
        expect(() => SegmentDetailsSchema.parse(segment)).not.toThrow();
    });

    it('rejects invalid confidence_level', () => {
        const segment = {
            segment_name: 'Urban_Peak_Premium',
            cluster_id: 2,
            characteristics: {},
            centroid_distance: 0.45,
            human_readable_description: 'High-demand urban area',
            confidence_level: 'very_high',
        };
        expect(() => SegmentDetailsSchema.parse(segment)).toThrow();
    });

    it('rejects negative cluster_id', () => {
        const segment = {
            segment_name: 'Urban_Peak_Premium',
            cluster_id: -1,
            characteristics: {},
            centroid_distance: 0.45,
            human_readable_description: 'High-demand urban area',
            confidence_level: 'high',
        };
        expect(() => SegmentDetailsSchema.parse(segment)).toThrow();
    });

    it('rejects negative centroid_distance', () => {
        const segment = {
            segment_name: 'Urban_Peak_Premium',
            cluster_id: 2,
            characteristics: {},
            centroid_distance: -0.1,
            human_readable_description: 'High-demand urban area',
            confidence_level: 'high',
        };
        expect(() => SegmentDetailsSchema.parse(segment)).toThrow();
    });
});

describe('PricingResultSchema', () => {
    const validSegment = {
        segment_name: 'Urban_Peak_Premium',
        cluster_id: 2,
        characteristics: { avg_supply_demand_ratio: 0.65 },
        centroid_distance: 0.45,
        human_readable_description: 'High-demand urban area',
        confidence_level: 'high' as const,
    };

    const validPricingResult = {
        recommended_price: 42.5,
        confidence_score: 0.85,
        expected_demand: 0.72,
        expected_profit: 15.3,
        baseline_profit: 10.5,
        profit_uplift_percent: 45.71,
        segment: validSegment,
        model_used: 'xgboost',
        rules_applied: [],
        price_before_rules: 38.5,
        price_demand_curve: [],
        processing_time_ms: 245.5,
        timestamp: '2024-01-15T10:30:00Z',
    };

    it('validates correct input', () => {
        expect(() => PricingResultSchema.parse(validPricingResult)).not.toThrow();
    });

    it('rejects negative recommended_price', () => {
        const invalid = { ...validPricingResult, recommended_price: -10 };
        expect(() => PricingResultSchema.parse(invalid)).toThrow();
    });

    it('rejects confidence_score > 1', () => {
        const invalid = { ...validPricingResult, confidence_score: 1.5 };
        expect(() => PricingResultSchema.parse(invalid)).toThrow();
    });

    it('rejects confidence_score < 0', () => {
        const invalid = { ...validPricingResult, confidence_score: -0.1 };
        expect(() => PricingResultSchema.parse(invalid)).toThrow();
    });

    it('rejects expected_demand > 1', () => {
        const invalid = { ...validPricingResult, expected_demand: 1.5 };
        expect(() => PricingResultSchema.parse(invalid)).toThrow();
    });

    it('rejects invalid timestamp format', () => {
        const invalid = { ...validPricingResult, timestamp: 'not-a-date' };
        expect(() => PricingResultSchema.parse(invalid)).toThrow();
    });

    it('defaults rules_applied to empty array', () => {
        const withoutRules = { ...validPricingResult };
        delete (withoutRules as Record<string, unknown>).rules_applied;
        const parsed = PricingResultSchema.parse(withoutRules);
        expect(parsed.rules_applied).toEqual([]);
    });

    it('validates with applied rules', () => {
        const withRules = {
            ...validPricingResult,
            rules_applied: [
                {
                    rule_id: 'floor_minimum_margin',
                    rule_name: 'Minimum Margin Floor',
                    price_before: 38.5,
                    price_after: 42.5,
                    impact: 4.0,
                    impact_percent: 10.39,
                },
            ],
        };
        expect(() => PricingResultSchema.parse(withRules)).not.toThrow();
    });
});

