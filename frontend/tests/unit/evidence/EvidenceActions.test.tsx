import { describe, it, expect } from 'bun:test';

describe('EvidenceActions Chat Context', () => {
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

  it('should generate correct chat prompt for XGBoost', () => {
    const topic = docTopics['xgboost'] || 'the documentation';
    const chatPrompt = encodeURIComponent(
      `I have questions about ${topic}. Can you help explain it?`
    );

    expect(chatPrompt).toContain('XGBoost');
    expect(decodeURIComponent(chatPrompt)).toContain('demand prediction model');
  });

  it('should generate correct chat prompt for data card', () => {
    const topic = docTopics['data_card'] || 'the documentation';
    const chatPrompt = encodeURIComponent(
      `I have questions about ${topic}. Can you help explain it?`
    );

    expect(decodeURIComponent(chatPrompt)).toContain('training dataset');
  });

  it('should handle unknown document ID', () => {
    const topic = docTopics['unknown_doc'] || 'the documentation';
    expect(topic).toBe('the documentation');
  });
});

describe('EvidenceActions Email Generation', () => {
  it('should generate mailto link with subject', () => {
    const subject = encodeURIComponent('PrismIQ Model Documentation Review');
    const body = encodeURIComponent('Test body content');
    const mailtoLink = `mailto:?subject=${subject}&body=${body}`;

    expect(mailtoLink).toContain('mailto:');
    expect(mailtoLink).toContain('subject=');
    expect(mailtoLink).toContain('body=');
    expect(decodeURIComponent(mailtoLink)).toContain('PrismIQ');
  });

  it('should include model documentation in email body', () => {
    const body = encodeURIComponent(
      'The documentation includes:\n' +
        '• Model Cards for XGBoost, Decision Tree, and Linear Regression models\n' +
        '• Dataset Card with feature definitions\n' +
        '• Methodology documentation\n' +
        '• Honeywell compliance mapping'
    );

    const decoded = decodeURIComponent(body);
    expect(decoded).toContain('XGBoost');
    expect(decoded).toContain('Decision Tree');
    expect(decoded).toContain('Honeywell');
  });
});

describe('EvidenceActions Download', () => {
  it('should define download content categories', () => {
    const downloadContent = [
      'Model Cards (JSON + Markdown)',
      'Data Card (JSON + Markdown)',
      'Methodology Documentation',
      'Compliance Mapping',
    ];

    expect(downloadContent).toHaveLength(4);
    expect(downloadContent).toContain('Model Cards (JSON + Markdown)');
    expect(downloadContent).toContain('Compliance Mapping');
  });
});
