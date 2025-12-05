'use client';

import { useState, type FC } from 'react';
import Link from 'next/link';
import JSZip from 'jszip';
import { MessageCircle, Mail, Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { toast } from '@/components/ui/toast';
import { DOC_TREE, type EvidenceResponse } from './types';

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

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const EvidenceActions: FC<EvidenceActionsProps> = ({ selectedDocId }) => {
  const [isDownloading, setIsDownloading] = useState(false);
  
  const topic = docTopics[selectedDocId] || 'the documentation';
  const chatPrompt = encodeURIComponent(
    `I have questions about ${topic}. Can you help explain it?`
  );

  const handleDownloadAll = async () => {
    setIsDownloading(true);
    toast.info('Preparing documentation package...');

    try {
      // Fetch all evidence data from the API
      const response = await fetch(`${API_BASE}/api/v1/evidence`);
      if (!response.ok) {
        throw new Error('Failed to fetch evidence data');
      }
      const evidence: EvidenceResponse = await response.json();

      // Create a new ZIP file
      const zip = new JSZip();

      // Create folder structure
      const modelsFolder = zip.folder('models');
      const dataFolder = zip.folder('data');
      const methodologyFolder = zip.folder('methodology');
      const complianceFolder = zip.folder('compliance');

      // Add Model Cards (JSON and Markdown)
      for (const card of evidence.model_cards) {
        const fileName = card.model_name.toLowerCase().replace(/\s+/g, '_');
        
        // JSON version
        modelsFolder?.file(
          `${fileName}_card.json`,
          JSON.stringify(card, null, 2)
        );

        // Markdown version
        const markdown = generateModelCardMarkdown(card);
        modelsFolder?.file(`${fileName}_card.md`, markdown);
      }

      // Add Data Card
      if (evidence.data_card) {
        dataFolder?.file(
          'dataset_card.json',
          JSON.stringify(evidence.data_card, null, 2)
        );
        
        const dataMarkdown = generateDataCardMarkdown(evidence.data_card);
        dataFolder?.file('dataset_card.md', dataMarkdown);
      }

      // Add Methodology documents (markdown)
      if (evidence.markdown_content) {
        for (const [docId, content] of Object.entries(evidence.markdown_content)) {
          const category = DOC_TREE.find((cat) =>
            cat.items.some((item) => item.id === docId)
          );
          
          let folder = methodologyFolder;
          if (category?.category === 'Compliance') {
            folder = complianceFolder;
          } else if (category?.category === 'Data Documentation') {
            folder = dataFolder;
          }

          const item = category?.items.find((i) => i.id === docId);
          const fileName = item?.label.toLowerCase().replace(/\s+/g, '_') || docId;
          folder?.file(`${fileName}.md`, content);
        }
      }

      // Add a README
      const readme = generateReadme();
      zip.file('README.md', readme);

      // Generate and download the ZIP
      const blob = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `PrismIQ_Documentation_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success('Documentation package downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download documentation. Please try again.');
    } finally {
      setIsDownloading(false);
    }
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
          disabled={isDownloading}
        >
          {isDownloading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          {isDownloading ? 'Preparing...' : 'Download All (ZIP)'}
        </Button>
      </div>
    </div>
  );
};

// Helper function to generate Model Card markdown
function generateModelCardMarkdown(card: EvidenceResponse['model_cards'][0]): string {
  return `# ${card.model_name}

**Version:** ${card.model_version}  
**Generated:** ${card.generated_at}

## Model Details

- **Architecture:** ${card.model_details.architecture}
- **Framework:** ${card.model_details.framework}
- **Training Date:** ${card.model_details.training_date}

### Hyperparameters

${Object.entries(card.model_details.hyperparameters)
  .map(([key, value]) => `- **${key}:** ${value}`)
  .join('\n')}

### Input Features

${card.model_details.input_features.map((f) => `- ${f}`).join('\n')}

### Output

${card.model_details.output}

## Performance Metrics

| Metric | Value |
|--------|-------|
| R² Score | ${(card.metrics.r2_score * 100).toFixed(2)}% |
| MAE | ${card.metrics.mae.toFixed(4)} |
| RMSE | ${card.metrics.rmse.toFixed(4)} |
| Test Set Size | ${card.metrics.test_set_size.toLocaleString()} |

## Intended Use

**Primary Use:** ${card.intended_use.primary_use}

**Target Users:**
${card.intended_use.users.map((u) => `- ${u}`).join('\n')}

**Out of Scope:**
${card.intended_use.out_of_scope.map((o) => `- ${o}`).join('\n')}

## Training Data

- **Dataset:** ${card.training_data.dataset_name}
- **Size:** ${card.training_data.dataset_size.toLocaleString()} records
- **Train/Test Split:** ${card.training_data.train_test_split}
- **Target Variable:** ${card.training_data.target_variable}

**Features Used:**
${card.training_data.features_used.map((f) => `- ${f}`).join('\n')}

## Feature Importance

| Feature | Importance |
|---------|------------|
${Object.entries(card.feature_importance)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 10)
  .map(([feature, importance]) => `| ${feature} | ${(importance * 100).toFixed(2)}% |`)
  .join('\n')}

## Ethical Considerations

### Fairness
${card.ethical_considerations.fairness_considerations.map((c) => `- ${c}`).join('\n')}

### Privacy
${card.ethical_considerations.privacy_considerations.map((c) => `- ${c}`).join('\n')}

### Transparency
${card.ethical_considerations.transparency_notes.map((c) => `- ${c}`).join('\n')}

## Limitations

${card.limitations.map((l) => `- ${l}`).join('\n')}

---
*Generated by PrismIQ*
`;
}

// Helper function to generate Data Card markdown
function generateDataCardMarkdown(card: EvidenceResponse['data_card']): string {
  return `# ${card.dataset_name}

**Version:** ${card.version}  
**Generated:** ${card.generated_at}

## Overview

${card.intended_use}

## Source Information

- **Origin:** ${card.source.origin}
- **Collection Date:** ${card.source.collection_date}

### Preprocessing Steps

${card.source.preprocessing_steps.map((s, i) => `${i + 1}. ${s}`).join('\n')}

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Row Count | ${card.statistics.row_count.toLocaleString()} |
| Column Count | ${card.statistics.column_count} |
| Missing Values | ${card.statistics.missing_values} |
| Numeric Features | ${card.statistics.numeric_features} |
| Categorical Features | ${card.statistics.categorical_features} |

## Features

| Feature | Type | Description | Range/Values | Distribution |
|---------|------|-------------|--------------|--------------|
${card.features
  .map(
    (f) =>
      `| ${f.name} | ${f.dtype} | ${f.description} | ${f.range_or_values} | ${f.distribution} |`
  )
  .join('\n')}

## Known Biases

${card.known_biases.length > 0 ? card.known_biases.map((b) => `- ${b}`).join('\n') : '*No known biases documented*'}

## Limitations

${card.limitations.map((l) => `- ${l}`).join('\n')}

---
*Generated by PrismIQ*
`;
}

// Helper function to generate README
function generateReadme(): string {
  return `# PrismIQ Documentation Package

This package contains all documentation for the PrismIQ dynamic pricing system.

## Contents

### /models
- Model cards for all ML models (XGBoost, Decision Tree, Linear Regression)
- Both JSON and Markdown formats included

### /data
- Dataset card with feature definitions
- Data quality and statistics information

### /methodology
- Pricing algorithm documentation
- Demand modeling methodology
- Business rules engine specification

### /compliance
- Audit trail documentation
- Honeywell enterprise mapping

## Usage

These documents are designed to provide transparency into PrismIQ's pricing decisions. 
They follow industry standards for ML model documentation (Model Cards) and can be 
used for:

- Regulatory compliance reviews
- Executive briefings
- Technical audits
- Stakeholder communication

## Questions?

Contact the PrismIQ team or use the chat interface in the application for 
real-time assistance.

---
*Generated on ${new Date().toLocaleDateString()}*
*PrismIQ - Intelligent Dynamic Pricing*
`;
}
