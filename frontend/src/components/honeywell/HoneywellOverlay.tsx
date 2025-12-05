'use client';

import type { FC } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Download, X, Factory } from 'lucide-react';
import { useLayoutStore } from '@/stores/layoutStore';
import { MappingTable } from './MappingTable';
import { toast } from '@/components/ui/toast';
import { generateHoneywellPDF } from './generateHoneywellPDF';

export const HoneywellOverlay: FC = () => {
  const { isHoneywellOpen, setHoneywellOpen } = useLayoutStore();

  const handleDownloadPDF = async () => {
    toast.info('Generating Honeywell Mapping PDF...');
    try {
      await generateHoneywellPDF();
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF. Please try again.');
    }
  };

  return (
    <Dialog open={isHoneywellOpen} onOpenChange={setHoneywellOpen}>
      <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Factory className="h-5 w-5 text-primary" />
            Ride-Sharing to Honeywell Enterprise Mapping
          </DialogTitle>
          <DialogDescription>
            How PrismIQ's dynamic pricing concepts translate to enterprise
            manufacturing and supply chain applications
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto py-4">
          <MappingTable />
        </div>

        <div className="flex-shrink-0 flex justify-between items-center pt-4 border-t">
          <p className="text-xs text-muted-foreground">
            This mapping demonstrates the transferability of our AI-powered
            pricing to Honeywell's enterprise solutions.
          </p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleDownloadPDF}>
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
            <Button onClick={() => setHoneywellOpen(false)}>
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

