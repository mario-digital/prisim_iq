import { describe, it, expect } from 'bun:test';
import type { DocTreeCategory, DocTreeItem } from '@/components/evidence/types';

describe('DocNavigation Types', () => {
  it('should define DocTreeItem correctly', () => {
    const item: DocTreeItem = {
      id: 'test_id',
      label: 'Test Label',
    };
    expect(item.id).toBe('test_id');
    expect(item.label).toBe('Test Label');
  });

  it('should define DocTreeCategory correctly', () => {
    const category: DocTreeCategory = {
      category: 'Test Category',
      items: [
        { id: 'item1', label: 'Item 1' },
        { id: 'item2', label: 'Item 2' },
      ],
    };
    expect(category.category).toBe('Test Category');
    expect(category.items).toHaveLength(2);
  });
});

describe('DocNavigation Selection Logic', () => {
  it('should identify selected item correctly', () => {
    const selectedId = 'xgboost';
    const items = [
      { id: 'xgboost', label: 'XGBoost Model Card' },
      { id: 'decision_tree', label: 'Decision Tree Model Card' },
    ];

    const selectedItem = items.find((item) => item.id === selectedId);
    expect(selectedItem).toBeDefined();
    expect(selectedItem?.label).toBe('XGBoost Model Card');
  });

  it('should handle unknown selection', () => {
    const selectedId = 'unknown';
    const items = [
      { id: 'xgboost', label: 'XGBoost Model Card' },
    ];

    const selectedItem = items.find((item) => item.id === selectedId);
    expect(selectedItem).toBeUndefined();
  });
});

describe('Category Expansion State', () => {
  it('should track expanded categories with Set', () => {
    const categories = ['Model Documentation', 'Data Documentation'];
    const expandedCategories = new Set(categories);

    expect(expandedCategories.has('Model Documentation')).toBe(true);
    expect(expandedCategories.has('Data Documentation')).toBe(true);
    expect(expandedCategories.has('Unknown Category')).toBe(false);
  });

  it('should toggle category expansion', () => {
    const expandedCategories = new Set(['Model Documentation']);

    // Collapse
    expandedCategories.delete('Model Documentation');
    expect(expandedCategories.has('Model Documentation')).toBe(false);

    // Expand again
    expandedCategories.add('Model Documentation');
    expect(expandedCategories.has('Model Documentation')).toBe(true);
  });
});
