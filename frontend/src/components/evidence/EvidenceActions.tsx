'use client';

import type { FC } from 'react';
import Link from 'next/link';
import { MessageCircle, Mail, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface EvidenceActionsProps {
  selectedDocId: string;
}

// Map doc IDs to topic names for chat context
const docTopics: Record<string, string> = {
  xgboost: 'XGBoost demand prediction model',
  decision_tree: 'Decision Tree model',
  linear_regression: 'Linear Regression model',
  data_card: 'training dataset',
  feature_definitions: 'feature definitions',
  pricing_algorithm: 'pricing algorithm',
  demand_modeling: 'demand modeling methodology',
  rules_engine: 'business rules engine',
  audit_trail: 'audit trail',
  honeywell_mapping: 'Honeywell compliance mapping',
};

export const EvidenceActions: FC<EvidenceActionsProps> = ({ selectedDocId }) => {
  const topic = docTopics[selectedDocId] || 'the documentation';
  const chatPrompt = encodeURIComponent(
    `I have questions about ${topic}. Can you help explain it?`
  );

  const handleDownloadAll = async () => {
    // Mock implementation - in production, this would call an API endpoint
    // that generates a ZIP file of all documentation
    alert(
      'Download All: This feature will export all documentation as a ZIP file.\n\n' +
        'In production, this would call the backend to generate and download:\n' +
        '• Model Cards (JSON + Markdown)\n' +
        '• Data Card (JSON + Markdown)\n' +
        '• Methodology Documentation\n' +
        '• Compliance Mapping'
    );
  };

  const handleEmailExecutives = () => {
    const subject = encodeURIComponent('PrismIQ Model Documentation Review');
    const body = encodeURIComponent(
      'Dear Team,\n\n' +
        'I would like to share the PrismIQ model documentation for your review.\n\n' +
        'The documentation includes:\n' +
        '• Model Cards for XGBoost, Decision Tree, and Linear Regression models\n' +
        '• Dataset Card with feature definitions and data quality information\n' +
        '• Methodology documentation for pricing algorithms\n' +
        '• Honeywell compliance mapping\n\n' +
        'Please let me know if you have any questions.\n\n' +
        'Best regards'
    );
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  return (
    <div className="pt-4 space-y-3">
      <Separator />
      <div className="space-y-2">
        <Button variant="outline" className="w-full justify-start gap-2" asChild>
          <Link href={`/workspace?prompt=${chatPrompt}`}>
            <MessageCircle className="h-4 w-4" />
            Questions? Open Chat
          </Link>
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-2"
          onClick={handleEmailExecutives}
        >
          <Mail className="h-4 w-4" />
          Email to Executives
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-2"
          onClick={handleDownloadAll}
        >
          <Download className="h-4 w-4" />
          Download All (ZIP)
        </Button>
      </div>
    </div>
  );
};


