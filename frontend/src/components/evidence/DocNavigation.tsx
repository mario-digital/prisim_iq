'use client';

import { useState } from 'react';
import type { FC } from 'react';
import { ChevronDown, ChevronRight, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DOC_TREE } from './types';

interface DocNavigationProps {
  selectedId: string;
  onSelect: (id: string) => void;
}

export const DocNavigation: FC<DocNavigationProps> = ({
  selectedId,
  onSelect,
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(DOC_TREE.map((c) => c.category))
  );

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  return (
    <nav className="space-y-2" aria-label="Documentation navigation">
      <h3 className="text-sm font-semibold text-foreground mb-4">
        Documentation
      </h3>
      {DOC_TREE.map((category) => {
        const isExpanded = expandedCategories.has(category.category);
        return (
          <div key={category.category} className="space-y-1">
            <button
              onClick={() => toggleCategory(category.category)}
              className="flex items-center gap-2 w-full text-left px-2 py-1.5 rounded text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
              aria-expanded={isExpanded}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 shrink-0" />
              ) : (
                <ChevronRight className="h-4 w-4 shrink-0" />
              )}
              {category.category}
            </button>
            {isExpanded && (
              <ul className="ml-4 space-y-0.5">
                {category.items.map((item) => (
                  <li key={item.id}>
                    <button
                      onClick={() => onSelect(item.id)}
                      className={cn(
                        'flex items-center gap-2 w-full text-left px-3 py-2 rounded text-sm transition-colors',
                        selectedId === item.id
                          ? 'bg-primary/10 text-primary font-medium'
                          : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                      )}
                      aria-current={selectedId === item.id ? 'page' : undefined}
                    >
                      <FileText className="h-4 w-4 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </nav>
  );
};
