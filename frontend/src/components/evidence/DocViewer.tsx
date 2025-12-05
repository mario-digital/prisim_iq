'use client';

import type { FC, ReactNode } from 'react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  FileText,
  Hash,
  Code2,
  Quote,
  ArrowRight,
  Sparkles,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getMetricTooltip, getValueTooltip } from './tooltipDefinitions';

interface DocViewerProps {
  content: string;
  isLoading: boolean;
}

/**
 * Documentation tooltips for common terms found in model/data cards
 */
const docTermTooltips: Record<string, { term: string; description: string }> = {
  // Model metrics
  'r² score': {
    term: 'R² Score',
    description:
      'Coefficient of determination. Measures how well the model explains variance. 1.0 is perfect, 0.98 means 98% of variance explained.',
  },
  'mae': {
    term: 'Mean Absolute Error',
    description:
      'Average prediction error in the same units as demand. Lower is better.',
  },
  'rmse': {
    term: 'Root Mean Square Error',
    description:
      'Prediction accuracy metric that penalizes larger errors more. Lower is better.',
  },
  'mse': {
    term: 'Mean Squared Error',
    description:
      'Average of squared prediction errors. Related to RMSE (RMSE = √MSE).',
  },
  // Model types
  'xgboost': {
    term: 'XGBoost',
    description:
      'Extreme Gradient Boosting - an ensemble learning algorithm that builds decision trees sequentially, with each tree correcting errors from the previous ones.',
  },
  'random forest': {
    term: 'Random Forest',
    description:
      'An ensemble method that creates many decision trees and combines their predictions. Robust against overfitting.',
  },
  'linear regression': {
    term: 'Linear Regression',
    description:
      'A simple statistical model that assumes a linear relationship between inputs and output. Highly interpretable.',
  },
  'gradient boosting': {
    term: 'Gradient Boosting',
    description:
      'Machine learning technique that builds models sequentially, with each new model correcting errors from previous ones.',
  },
  // Data terms
  'training data': {
    term: 'Training Data',
    description:
      'Historical data used to teach the model patterns. More data generally leads to better predictions.',
  },
  'test data': {
    term: 'Test Data',
    description:
      'Data held back from training to evaluate model performance on unseen examples.',
  },
  'feature': {
    term: 'Feature',
    description:
      'An input variable used by the model for predictions (e.g., price, location, time).',
  },
  'target': {
    term: 'Target Variable',
    description:
      'The value the model is trying to predict (in our case, demand).',
  },
  // Pricing terms
  'demand elasticity': {
    term: 'Demand Elasticity',
    description:
      'How sensitive demand is to price changes. Higher elasticity means demand changes more with price.',
  },
  'surge pricing': {
    term: 'Surge Pricing',
    description:
      'Dynamic pricing that increases prices during high-demand periods to balance supply and demand.',
  },
  'baseline price': {
    term: 'Baseline Price',
    description:
      'The starting reference price before any optimizations or adjustments are applied.',
  },
  // Business rules
  'surge cap': {
    term: 'Surge Cap',
    description:
      'Maximum allowed price multiplier during high-demand periods. Protects customers from extreme pricing.',
  },
  'loyalty discount': {
    term: 'Loyalty Discount',
    description:
      'Price reduction for returning customers based on their loyalty tier (Bronze, Silver, Gold).',
  },
};

/**
 * Get tooltip for a table cell based on its text content
 */
const getCellTooltip = (text: string): { term: string; description: string } | null => {
  const lowerText = text.toLowerCase().trim();

  // Check for exact matches first
  if (docTermTooltips[lowerText]) {
    return docTermTooltips[lowerText];
  }

  // Check for partial matches
  for (const [key, tooltip] of Object.entries(docTermTooltips)) {
    if (lowerText.includes(key) || key.includes(lowerText)) {
      return tooltip;
    }
  }

  // Check metric tooltips
  const metricTooltip = getMetricTooltip(lowerText.replace(/[^a-z0-9_]/g, '_'));
  if (metricTooltip) {
    return { term: metricTooltip.metric, description: metricTooltip.description };
  }

  return null;
};

/**
 * Check if a value looks like a metric value (number, percentage, etc.)
 */
const isMetricValue = (text: string): boolean => {
  const trimmed = text.trim();
  // Check for numbers, percentages, decimals
  return /^[\d.,]+%?$/.test(trimmed) || /^\d+\.\d+$/.test(trimmed);
};

/**
 * Get interpretation for a metric value based on context
 */
const getValueInterpretation = (text: string, rowContext: string): string => {
  const numValue = parseFloat(text.replace(/[%,]/g, ''));

  if (rowContext.toLowerCase().includes('r²') || rowContext.toLowerCase().includes('r2')) {
    if (numValue >= 0.95) return 'Excellent - captures nearly all variance';
    if (numValue >= 0.85) return 'Good - highly predictive model';
    if (numValue >= 0.7) return 'Moderate - acceptable performance';
    return 'Lower - may need improvement';
  }

  if (rowContext.toLowerCase().includes('mae') || rowContext.toLowerCase().includes('error')) {
    if (numValue <= 0.02) return 'Very accurate predictions';
    if (numValue <= 0.05) return 'Good accuracy';
    return 'Higher error - consider carefully';
  }

  if (rowContext.toLowerCase().includes('rmse')) {
    if (numValue <= 0.03) return 'Excellent consistency';
    if (numValue <= 0.08) return 'Good consistency';
    return 'Higher variance in predictions';
  }

  return `Value: ${text}`;
};

/**
 * Skeleton loader that mimics typical markdown document layout.
 */
function DocumentSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <Skeleton className="h-9 w-2/3" />
      <div className="flex gap-4">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="h-px w-full" />
      <div className="space-y-3 pt-2">
        <Skeleton className="h-7 w-1/3" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-11/12" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </div>
      <div className="space-y-3 pt-4">
        <Skeleton className="h-7 w-2/5" />
        <div className="space-y-2 pl-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <Skeleton className="h-2 w-2 rounded-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </div>
      </div>
      <div className="space-y-3 pt-4">
        <Skeleton className="h-7 w-1/4" />
        <div className="border rounded-lg overflow-hidden">
          <div className="flex gap-2 p-3 bg-muted/30">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-4 w-1/3" />
          </div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-2 p-3 border-t">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Table cell with optional tooltip
 */
const TooltipCell: FC<{
  children: ReactNode;
  isHeader?: boolean;
  rowContext?: string;
}> = ({ children, isHeader = false, rowContext = '' }) => {
  const text = String(children);
  const tooltip = getCellTooltip(text);
  const isValue = isMetricValue(text);

  // If we have a tooltip or it's a recognizable value, wrap in tooltip
  if (tooltip || (isValue && rowContext)) {
    const interpretation = isValue ? getValueInterpretation(text, rowContext) : '';

    return (
      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="cursor-help hover:text-primary transition-colors inline-flex items-center gap-1">
              {children}
              <HelpCircle className="h-3 w-3 opacity-40 hover:opacity-70" />
            </span>
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-[280px]">
            {tooltip ? (
              <>
                <p className="font-semibold text-xs mb-1">{tooltip.term}</p>
                <p className="text-xs opacity-80">{tooltip.description}</p>
              </>
            ) : (
              <p className="text-xs">{interpretation}</p>
            )}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return <>{children}</>;
};

export const DocViewer: FC<DocViewerProps> = ({ content, isLoading }) => {
  // Track current row context for value interpretation
  const [currentRowMetric, setCurrentRowMetric] = useState('');

  if (isLoading) {
    return <DocumentSkeleton />;
  }

  if (!content) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center mb-4">
          <FileText className="h-8 w-8 text-primary" />
        </div>
        <p className="text-muted-foreground">
          Select a document from the navigation to view its contents.
        </p>
      </div>
    );
  }

  return (
    <article className="prose prose-slate dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // H1 - Document title with gradient
          h1({ children, ...props }) {
            return (
              <h1
                className="not-prose text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent mb-2 flex items-center gap-3"
                {...props}
              >
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-4 w-4 text-primary-foreground" />
                </div>
                {children}
              </h1>
            );
          },
          // H2 - Section headers with accent bar
          h2({ children, ...props }) {
            return (
              <h2
                className="not-prose text-lg font-semibold text-foreground mt-8 mb-4 flex items-center gap-2 group"
                {...props}
              >
                <div className="h-6 w-1 rounded-full bg-gradient-to-b from-primary to-primary/40" />
                {children}
              </h2>
            );
          },
          // H3 - Subsection headers
          h3({ children, ...props }) {
            return (
              <h3
                className="not-prose text-base font-medium text-foreground/90 mt-6 mb-3 flex items-center gap-2"
                {...props}
              >
                <Hash className="h-4 w-4 text-primary/60" />
                {children}
              </h3>
            );
          },
          // Paragraphs
          p({ children, ...props }) {
            return (
              <p
                className="not-prose text-sm text-muted-foreground leading-relaxed mb-4"
                {...props}
              >
                {children}
              </p>
            );
          },
          // Strong/bold text
          strong({ children, ...props }) {
            return (
              <strong className="font-semibold text-foreground" {...props}>
                {children}
              </strong>
            );
          },
          // Unordered lists
          ul({ children, ...props }) {
            return (
              <ul className="not-prose space-y-2 my-4" {...props}>
                {children}
              </ul>
            );
          },
          // Ordered lists
          ol({ children, ...props }) {
            return (
              <ol
                className="not-prose space-y-2 my-4 counter-reset-item"
                {...props}
              >
                {children}
              </ol>
            );
          },
          // List items with custom bullets
          li({ children, ...props }) {
            return (
              <li
                className="flex items-start gap-3 text-sm text-muted-foreground"
                {...props}
              >
                <ArrowRight className="h-4 w-4 text-primary/60 flex-shrink-0 mt-0.5" />
                <span className="flex-1">{children}</span>
              </li>
            );
          },
          // Code blocks with header
          code({ className, children, ...props }) {
            const isInline = !className;
            if (isInline) {
              return (
                <code
                  className="not-prose px-1.5 py-0.5 rounded bg-primary/10 text-primary text-sm font-mono"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <code
                className="block text-sm font-mono text-foreground/90"
                {...props}
              >
                {children}
              </code>
            );
          },
          // Pre blocks (code containers)
          pre({ children, ...props }) {
            return (
              <div className="not-prose my-4 rounded-lg border border-border overflow-hidden bg-card">
                <div className="flex items-center gap-2 px-4 py-2 bg-muted/50 border-b border-border">
                  <Code2 className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs font-medium text-muted-foreground">
                    Code
                  </span>
                </div>
                <pre className="p-4 overflow-x-auto bg-muted/30" {...props}>
                  {children}
                </pre>
              </div>
            );
          },
          // Tables - modern card design with tooltips
          table({ children, ...props }) {
            return (
              <div className="not-prose overflow-x-auto my-6 rounded-xl border border-border bg-card shadow-sm">
                <table className="w-full text-sm" {...props}>
                  {children}
                </table>
              </div>
            );
          },
          thead({ children, ...props }) {
            return (
              <thead
                className="bg-gradient-to-r from-muted/80 to-muted/40"
                {...props}
              >
                {children}
              </thead>
            );
          },
          th({ children, ...props }) {
            return (
              <th
                className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                {...props}
              >
                <TooltipCell isHeader>{children}</TooltipCell>
              </th>
            );
          },
          tbody({ children, ...props }) {
            return (
              <tbody className="divide-y divide-border/50" {...props}>
                {children}
              </tbody>
            );
          },
          tr({ children, ...props }) {
            // Extract first cell text for context
            let rowMetric = '';
            if (Array.isArray(children)) {
              const firstChild = children[0];
              if (firstChild && typeof firstChild === 'object' && 'props' in firstChild) {
                const cellChildren = firstChild.props?.children;
                if (typeof cellChildren === 'string') {
                  rowMetric = cellChildren;
                }
              }
            }

            return (
              <tr
                className="hover:bg-primary/5 transition-colors duration-150"
                data-row-metric={rowMetric}
                {...props}
              >
                {children}
              </tr>
            );
          },
          td({ children, ...props }) {
            // Get row context from parent tr if available
            const rowContext =
              (props as Record<string, unknown>)?.['data-row-metric'] || '';

            return (
              <td className="px-4 py-3.5 text-foreground" {...props}>
                <TooltipCell rowContext={String(rowContext)}>{children}</TooltipCell>
              </td>
            );
          },
          // Blockquotes with icon
          blockquote({ children, ...props }) {
            return (
              <blockquote
                className="not-prose my-6 rounded-lg border-l-4 border-primary/60 bg-primary/5 p-4 flex gap-3"
                {...props}
              >
                <Quote className="h-5 w-5 text-primary/60 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-foreground/80 italic">
                  {children}
                </div>
              </blockquote>
            );
          },
          // Horizontal rules - decorative divider
          hr(props) {
            return (
              <div
                className="not-prose my-8 flex items-center gap-4"
                {...props}
              >
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
                <div className="flex gap-1">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary/40" />
                  <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
                  <div className="h-1.5 w-1.5 rounded-full bg-primary/40" />
                </div>
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
              </div>
            );
          },
          // Links with hover effect
          a({ href, children, ...props }) {
            return (
              <a
                href={href}
                className="text-primary hover:text-primary/80 underline underline-offset-2 decoration-primary/30 hover:decoration-primary/60 transition-colors"
                target={href?.startsWith('http') ? '_blank' : undefined}
                rel={
                  href?.startsWith('http') ? 'noopener noreferrer' : undefined
                }
                {...props}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </article>
  );
};
