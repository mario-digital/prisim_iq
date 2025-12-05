'use client';

import { useState, type FC } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/toast';
import { Share2, Download, Loader2 } from 'lucide-react';
import { generateExecutivePDF } from '@/lib/generatePDF';
import type { ExecutiveData } from './mockData';

interface ExecutiveActionsProps {
  /** Executive data for PDF generation */
  data?: ExecutiveData | null;
  /** Optional callback for share action */
  onShare?: () => void;
  /** Optional callback for download action */
  onDownload?: () => void;
}

export const ExecutiveActions: FC<ExecutiveActionsProps> = ({
  data,
  onShare,
  onDownload,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleShare = () => {
    if (onShare) {
      onShare();
    } else {
      // Open mailto with report summary
      const subject = encodeURIComponent('PrismIQ Executive Report');
      const body = encodeURIComponent(
        `PrismIQ Dynamic Pricing Executive Summary\n\n` +
        `Overall Profit Uplift: +${data?.profitUplift ?? 24.3}%\n` +
        `Decisions Made: ${data?.recommendationsAnalyzed ?? 1247}\n` +
        `Compliance Rate: ${data?.complianceRate ?? 100}%\n\n` +
        `Please see the attached PDF for the full report.`
      );
      window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
  };

  const handleDownload = async () => {
    if (onDownload) {
      onDownload();
      return;
    }

    if (!data) {
      toast.error('No data available for PDF generation');
      return;
    }

    setIsGenerating(true);
    try {
      await generateExecutivePDF(data);
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex gap-3">
      <Button variant="outline" onClick={handleShare} className="flex-1">
        <Share2 className="h-4 w-4 mr-2" />
        Share Report
      </Button>
      <Button 
        onClick={handleDownload} 
        className="flex-1"
        disabled={isGenerating}
      >
        {isGenerating ? (
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        ) : (
          <Download className="h-4 w-4 mr-2" />
        )}
        {isGenerating ? 'Generating...' : 'Download PDF'}
      </Button>
    </div>
  );
};
