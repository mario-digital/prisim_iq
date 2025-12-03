import { describe, it, expect } from 'bun:test';
import type { DocTreeCategory, DocTreeItem } from '@/components/evidence/types';
import {
  DOC_TREE,
  DOC_IDS,
  getAllDocIds,
  validateDocTreeUniqueness,
} from '@/components/evidence/types';

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

describe('DOC_TREE Centralized Data', () => {
  it('should have all expected categories', () => {
    const categoryNames = DOC_TREE.map((c) => c.category);
    expect(categoryNames).toContain('Model Documentation');
    expect(categoryNames).toContain('Data Documentation');
    expect(categoryNames).toContain('Methodology');
    expect(categoryNames).toContain('Compliance');
  });

  it('should have unique IDs across the entire tree (CRITICAL)', () => {
    const { valid, duplicates } = validateDocTreeUniqueness();
    expect(duplicates).toEqual([]);
    expect(valid).toBe(true);
  });

  it('should have IDs matching DOC_IDS constant', () => {
    const treeIds = getAllDocIds();
    const constantIds = [...DOC_IDS];
    
    // Every tree ID should be in DOC_IDS
    for (const id of treeIds) {
      expect(constantIds).toContain(id);
    }
    
    // DOC_IDS and tree IDs should match in count
    expect(treeIds.length).toBe(constantIds.length);
  });

  it('should have non-empty labels for all items', () => {
    for (const category of DOC_TREE) {
      for (const item of category.items) {
        expect(item.label.length).toBeGreaterThan(0);
      }
    }
  });
});

describe('DocNavigation Selection Logic', () => {
  it('should identify selected item correctly using DOC_TREE', () => {
    const selectedId = 'xgboost';
    const allItems = DOC_TREE.flatMap((c) => c.items);
    
    const selectedItem = allItems.find((item) => item.id === selectedId);
    expect(selectedItem).toBeDefined();
    expect(selectedItem?.label).toBe('XGBoost Model Card');
  });

  it('should handle unknown selection', () => {
    const selectedId = 'unknown';
    const allItems = DOC_TREE.flatMap((c) => c.items);

    const selectedItem = allItems.find((item) => item.id === selectedId);
    expect(selectedItem).toBeUndefined();
  });
});

describe('Category Expansion State', () => {
  it('should track expanded categories with Set', () => {
    const categories = DOC_TREE.map((c) => c.category);
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
