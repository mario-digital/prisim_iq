'use client';

import type { FC } from 'react';
import { useCallback, useEffect, useState } from 'react';
import { Download } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useStatusStore } from '@/stores/statusStore';
import { getHoneywellMapping } from '@/services/evidenceService';
import type { HoneywellMappingResponse } from '@/services/evidenceService';
import { MappingTable } from './MappingTable';

/**
 * HoneywellOverlay displays a modal with the ride-sharing to Honeywell
 * enterprise concept mapping. Accessible from any tab via the toggle in header.
 *
 * Features:
 * - Dialog modal with accessibility (focus trap, aria labels)
 * - Close on X button and Escape key (built into Radix Dialog)
 * - Download PDF/text export of mapping data
 * - Persists across tab navigation (state in statusStore)
 */
export const HoneywellOverlay: FC = () => {
  const { honeywellOverlayVisible, setHoneywellOverlay } = useStatusStore();
  const [mapping, setMapping] = useState<HoneywellMappingResponse | null>(null);

  // Pre-fetch mapping data when overlay opens
  useEffect(() => {
    if (honeywellOverlayVisible && !mapping) {
      getHoneywellMapping().then(setMapping);
    }
  }, [honeywellOverlayVisible, mapping]);

  /**
   * Download the mapping as a text file.
   * For hackathon demo: exports as formatted text.
   * Production would generate actual PDF.
   */
  const handleDownloadPDF = useCallback(() => {
    if (!mapping) return;

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

    const blob = new Blob([fullContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'honeywell-mapping.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [mapping]);

  return (
    <Dialog open={honeywellOverlayVisible} onOpenChange={setHoneywellOverlay}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <span>🏭</span>
            Ride-Sharing to Honeywell Mapping
          </DialogTitle>
          <DialogDescription>
            How dynamic pricing concepts from ride-sharing translate to enterprise applications
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <MappingTable />
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleDownloadPDF}
            disabled={!mapping}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
          <Button onClick={() => setHoneywellOverlay(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

