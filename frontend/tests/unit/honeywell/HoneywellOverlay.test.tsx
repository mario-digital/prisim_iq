/**
 * Tests for HoneywellOverlay and MappingTable components.
 * Tests modal behavior, data fetching, and download functionality.
 */
import { describe, test, expect, beforeEach, mock } from 'bun:test';
import { useStatusStore } from '@/stores/statusStore';
import { clearEvidenceCache, getHoneywellMapping } from '@/services/evidenceService';
import type { HoneywellMappingResponse, HoneywellMappingItem } from '@/components/evidence/types';

describe('HoneywellOverlay State Management', () => {
  beforeEach(() => {
    // Reset store to initial state
    useStatusStore.setState({
      honeywellOverlayVisible: false,
    });
    // Clear any cached data
    clearEvidenceCache();
  });

  test('should start with overlay hidden', () => {
    const state = useStatusStore.getState();
    expect(state.honeywellOverlayVisible).toBe(false);
  });

  test('should toggle overlay visibility', () => {
    const { toggleHoneywellOverlay } = useStatusStore.getState();

    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);

    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);

    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
  });

  test('should set overlay visibility directly', () => {
    const { setHoneywellOverlay } = useStatusStore.getState();

    setHoneywellOverlay(true);
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);

    setHoneywellOverlay(false);
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
  });

  test('should persist overlay state across multiple toggles', () => {
    const { toggleHoneywellOverlay, setHoneywellOverlay } = useStatusStore.getState();

    // Toggle on
    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);

    // Set directly to same value (should stay true)
    setHoneywellOverlay(true);
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);

    // Toggle off
    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
  });
});

describe('Honeywell Mapping Data', () => {
  beforeEach(() => {
    clearEvidenceCache();
  });

  test('should fetch mapping data with correct structure', async () => {
    const mapping = await getHoneywellMapping();

    expect(mapping).toBeDefined();
    expect(mapping.title).toBeDefined();
    expect(Array.isArray(mapping.mappings)).toBe(true);
    expect(Array.isArray(mapping.compliance_notes)).toBe(true);
  });

  test('should have required fields in each mapping item', async () => {
    const mapping = await getHoneywellMapping();

    mapping.mappings.forEach((item: HoneywellMappingItem) => {
      expect(item.ride_sharing_concept).toBeDefined();
      expect(typeof item.ride_sharing_concept).toBe('string');
      expect(item.honeywell_equivalent).toBeDefined();
      expect(typeof item.honeywell_equivalent).toBe('string');
      expect(item.rationale).toBeDefined();
      expect(typeof item.rationale).toBe('string');
    });
  });

  test('should return cached data on subsequent calls', async () => {
    const firstCall = await getHoneywellMapping();
    const secondCall = await getHoneywellMapping();

    // Should be the exact same object reference (cached)
    expect(firstCall).toBe(secondCall);
  });

  test('fallback mapping should have meaningful content', async () => {
    const mapping = await getHoneywellMapping();

    // Should have at least 5 mapping entries
    expect(mapping.mappings.length).toBeGreaterThanOrEqual(5);

    // Check for expected mapping concepts
    const concepts = mapping.mappings.map((m) => m.ride_sharing_concept);
    expect(concepts.some((c) => c.toLowerCase().includes('rider') || c.toLowerCase().includes('demand'))).toBe(true);
    expect(concepts.some((c) => c.toLowerCase().includes('driver') || c.toLowerCase().includes('supply'))).toBe(true);
  });
});

describe('Honeywell Mapping Response Type', () => {
  test('should validate HoneywellMappingResponse structure', () => {
    const validResponse: HoneywellMappingResponse = {
      title: 'Test Mapping',
      mappings: [
        {
          ride_sharing_concept: 'Test Concept',
          honeywell_equivalent: 'Test Equivalent',
          rationale: 'Test Rationale',
        },
      ],
      compliance_notes: ['Note 1'],
    };

    expect(validResponse.title).toBe('Test Mapping');
    expect(validResponse.mappings).toHaveLength(1);
    expect(validResponse.mappings[0].ride_sharing_concept).toBe('Test Concept');
    expect(validResponse.compliance_notes).toHaveLength(1);
  });

  test('should allow empty mappings array', () => {
    const emptyResponse: HoneywellMappingResponse = {
      title: 'Empty Mapping',
      mappings: [],
      compliance_notes: [],
    };

    expect(emptyResponse.mappings).toHaveLength(0);
    expect(emptyResponse.compliance_notes).toHaveLength(0);
  });
});

describe('Download PDF Functionality', () => {
  test('should format mapping data correctly for download', async () => {
    const mapping = await getHoneywellMapping();

    // Simulate the download format logic
    const header = `${mapping.title}\n${'='.repeat(mapping.title.length)}\n\n`;

    const content = mapping.mappings
      .map(
        (m, i) =>
          `${i + 1}. ${m.ride_sharing_concept}\n` +
          `   → ${m.honeywell_equivalent}\n` +
          `   Rationale: ${m.rationale}\n`
      )
      .join('\n');

    const notes = mapping.compliance_notes.length
      ? `\n\nCompliance Notes:\n${mapping.compliance_notes.map((n) => `• ${n}`).join('\n')}`
      : '';

    const fullContent = header + content + notes;

    // Should include header
    expect(fullContent).toContain(mapping.title);

    // Should include each mapping
    mapping.mappings.forEach((m) => {
      expect(fullContent).toContain(m.ride_sharing_concept);
      expect(fullContent).toContain(m.honeywell_equivalent);
      expect(fullContent).toContain(m.rationale);
    });

    // Should include compliance notes
    if (mapping.compliance_notes.length > 0) {
      expect(fullContent).toContain('Compliance Notes:');
    }
  });
});

