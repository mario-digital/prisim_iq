'use client';

import type { FC } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { BusinessRule } from './types';

interface BusinessRulesListProps {
  rules: BusinessRule[];
}

/**
 * List of business rules that were evaluated with impact indicators.
 * Shows before/after prices and color-codes by rule type.
 */
export const BusinessRulesList: FC<BusinessRulesListProps> = ({ rules }) => {
  const triggeredRules = rules.filter((r) => r.triggered);
  const skippedRules = rules.filter((r) => !r.triggered);

  const getRuleTypeColor = (type: BusinessRule['type']) => {
    switch (type) {
      case 'floor':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'ceiling':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
      case 'margin':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'competitive':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      case 'promotional':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const getRuleTypeIcon = (type: BusinessRule['type']) => {
    switch (type) {
      case 'floor':
        return '⬆';
      case 'ceiling':
        return '⬇';
      case 'margin':
        return '📊';
      case 'competitive':
        return '🎯';
      case 'promotional':
        return '🏷';
      default:
        return '📋';
    }
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Business Rules</CardTitle>
          <span className="text-xs text-muted-foreground">
            {triggeredRules.length} applied / {rules.length} total
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {rules.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            No business rules configured
          </div>
        ) : (
          <>
            {/* Triggered rules */}
            {triggeredRules.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Applied Rules
                </div>
                {triggeredRules.map((rule, index) => (
                  <RuleItem key={`${rule.id}-${index}`} rule={rule} getRuleTypeColor={getRuleTypeColor} getRuleTypeIcon={getRuleTypeIcon} />
                ))}
              </div>
            )}

            {/* Skipped rules - collapsed */}
            {skippedRules.length > 0 && (
              <details className="group">
                <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground transition-colors list-none flex items-center gap-1">
                  <span className="group-open:rotate-90 transition-transform">▶</span>
                  {skippedRules.length} rules not triggered
                </summary>
                <div className="mt-2 space-y-2 pl-4 border-l-2 border-muted">
                  {skippedRules.map((rule, index) => (
                    <div
                      key={`${rule.id}-skipped-${index}`}
                      className="flex items-center gap-2 text-xs text-muted-foreground"
                    >
                      <span>{getRuleTypeIcon(rule.type)}</span>
                      <span>{rule.name}</span>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

interface RuleItemProps {
  rule: BusinessRule;
  getRuleTypeColor: (type: BusinessRule['type']) => string;
  getRuleTypeIcon: (type: BusinessRule['type']) => string;
}

const RuleItem: FC<RuleItemProps> = ({ rule, getRuleTypeColor, getRuleTypeIcon }) => {
  const impactIsPositive = rule.impact > 0;

  return (
    <div className="p-3 rounded-lg border bg-card">
      <div className="flex items-start justify-between gap-2">
        {/* Rule info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                getRuleTypeColor(rule.type)
              )}
            >
              {getRuleTypeIcon(rule.type)} {rule.type}
            </span>
            <span className="text-sm font-medium truncate">{rule.name}</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {rule.description}
          </p>
        </div>

        {/* Impact indicator */}
        <div className="text-right shrink-0">
          <div className="text-xs text-muted-foreground">Impact</div>
          <div
            className={cn(
              'text-sm font-semibold',
              impactIsPositive
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-red-600 dark:text-red-400'
            )}
          >
            {impactIsPositive ? '+' : ''}${rule.impact.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Before → After */}
      <div className="flex items-center gap-2 mt-2 pt-2 border-t text-xs">
        <span className="text-muted-foreground">
          ${rule.priceBefore.toFixed(2)}
        </span>
        <span className="text-muted-foreground">→</span>
        <span className="font-medium">${rule.priceAfter.toFixed(2)}</span>
      </div>
    </div>
  );
};

