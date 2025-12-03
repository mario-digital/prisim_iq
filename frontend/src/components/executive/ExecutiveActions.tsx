'use client';

import type { FC } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/toast';
import { Share2, Download } from 'lucide-react';

interface ExecutiveActionsProps {
  /** Optional callback for share action */
  onShare?: () => void;
  /** Optional callback for download action */
  onDownload?: () => void;
}

export const ExecutiveActions: FC<ExecutiveActionsProps> = ({
  onShare,
  onDownload,
}) => {
  const handleShare = () => {
    if (onShare) {
      onShare();
    } else {
      // Mock: Open mailto with report summary
      window.location.href =
        'mailto:?subject=PrismIQ Executive Report&body=Please find the executive summary attached.';
    }
  };

  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else {
      // Mock: Show toast notification for demo purposes
      toast.info('PDF download would be generated here. (Demo mode)');
    }
  };

  return (
    <div className="flex gap-3">
      <Button variant="outline" onClick={handleShare} className="flex-1">
        <Share2 className="h-4 w-4 mr-2" />
        Share Report
      </Button>
      <Button onClick={handleDownload} className="flex-1">
        <Download className="h-4 w-4 mr-2" />
        Download PDF
      </Button>
    </div>
  );
};

