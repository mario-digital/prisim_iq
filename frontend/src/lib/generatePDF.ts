import jsPDF from 'jspdf';
import type { ExecutiveData } from '@/components/executive/mockData';

/**
 * Generate a professional PDF report from executive data
 */
export async function generateExecutivePDF(data: ExecutiveData): Promise<void> {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;
  let y = margin;

  // Colors
  const primaryColor: [number, number, number] = [34, 211, 238]; // Cyan
  const textColor: [number, number, number] = [30, 41, 59]; // Slate-800
  const mutedColor: [number, number, number] = [100, 116, 139]; // Slate-500
  const successColor: [number, number, number] = [16, 185, 129]; // Emerald-500

  // Helper functions
  const addHeader = () => {
    // Logo/Brand
    doc.setFontSize(24);
    doc.setTextColor(...primaryColor);
    doc.setFont('helvetica', 'bold');
    doc.text('PrismIQ', margin, y);
    
    doc.setFontSize(10);
    doc.setTextColor(...mutedColor);
    doc.setFont('helvetica', 'normal');
    doc.text('Dynamic Pricing Intelligence', margin + 35, y);
    
    // Date
    doc.setFontSize(9);
    doc.text(new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    }), pageWidth - margin, y, { align: 'right' });
    
    y += 15;
    
    // Title
    doc.setFontSize(18);
    doc.setTextColor(...textColor);
    doc.setFont('helvetica', 'bold');
    doc.text('Executive Summary Report', margin, y);
    y += 12;
    
    // Divider
    doc.setDrawColor(...primaryColor);
    doc.setLineWidth(0.5);
    doc.line(margin, y, pageWidth - margin, y);
    y += 10;
  };

  const addSection = (title: string) => {
    doc.setFontSize(12);
    doc.setTextColor(...primaryColor);
    doc.setFont('helvetica', 'bold');
    doc.text(title, margin, y);
    y += 7;
  };

  const addMetric = (label: string, value: string, x: number, width: number) => {
    doc.setFontSize(9);
    doc.setTextColor(...mutedColor);
    doc.setFont('helvetica', 'normal');
    doc.text(label, x, y);
    
    doc.setFontSize(14);
    doc.setTextColor(...textColor);
    doc.setFont('helvetica', 'bold');
    doc.text(value, x, y + 6);
  };

  // Generate PDF content
  addHeader();

  // Hero Metric
  doc.setFillColor(240, 253, 250); // Emerald-50
  doc.roundedRect(margin, y, contentWidth, 25, 3, 3, 'F');
  
  doc.setFontSize(10);
  doc.setTextColor(...mutedColor);
  doc.setFont('helvetica', 'normal');
  doc.text('Overall Profit Uplift', margin + 5, y + 8);
  
  doc.setFontSize(22);
  doc.setTextColor(...successColor);
  doc.setFont('helvetica', 'bold');
  doc.text(`+${data.profitUplift}%`, margin + 5, y + 20);
  
  doc.setFontSize(9);
  doc.setTextColor(...mutedColor);
  doc.setFont('helvetica', 'normal');
  doc.text(`vs. $${data.baseline.toFixed(2)} baseline`, margin + 45, y + 20);
  
  y += 35;

  // Key Metrics Grid
  addSection('Key Performance Indicators');
  
  const metricsPerRow = 4;
  const metricWidth = contentWidth / metricsPerRow;
  
  data.metrics.slice(0, 8).forEach((metric, index) => {
    const col = index % metricsPerRow;
    const row = Math.floor(index / metricsPerRow);
    const x = margin + col * metricWidth;
    
    if (col === 0 && row > 0) {
      y += 18;
    }
    
    addMetric(metric.label, String(metric.value), x, metricWidth);
  });
  
  y += 25;

  // Key Insight
  addSection('Key Insight');
  
  doc.setFontSize(10);
  doc.setTextColor(...textColor);
  doc.setFont('helvetica', 'normal');
  
  // Remove markdown bold and wrap text
  const insightText = data.keyInsight.replace(/\*\*/g, '');
  const splitInsight = doc.splitTextToSize(insightText, contentWidth);
  doc.text(splitInsight, margin, y);
  y += splitInsight.length * 5 + 10;

  // Segment Performance
  addSection('Segment Performance');
  
  // Table header
  doc.setFillColor(241, 245, 249); // Slate-100
  doc.rect(margin, y, contentWidth, 8, 'F');
  
  doc.setFontSize(9);
  doc.setTextColor(...mutedColor);
  doc.setFont('helvetica', 'bold');
  doc.text('Segment', margin + 3, y + 5);
  doc.text('Baseline', margin + 60, y + 5);
  doc.text('Optimized', margin + 95, y + 5);
  doc.text('Improvement', margin + 135, y + 5);
  y += 10;
  
  // Table rows
  doc.setFont('helvetica', 'normal');
  data.segmentPerformance.forEach((segment, index) => {
    if (index % 2 === 0) {
      doc.setFillColor(248, 250, 252); // Slate-50
      doc.rect(margin, y - 4, contentWidth, 7, 'F');
    }
    
    doc.setTextColor(...textColor);
    doc.text(segment.segment, margin + 3, y);
    doc.text(`$${segment.baseline.toLocaleString()}`, margin + 60, y);
    doc.text(`$${segment.optimized.toLocaleString()}`, margin + 95, y);
    
    doc.setTextColor(...successColor);
    doc.text(`+${segment.improvement}%`, margin + 135, y);
    
    y += 7;
  });
  
  y += 10;

  // Model Performance
  addSection('Model Performance');
  
  doc.setFontSize(10);
  doc.setTextColor(...textColor);
  doc.setFont('helvetica', 'normal');
  doc.text(`Model Agreement: ${data.modelAgreement}%`, margin, y);
  y += 7;
  
  data.models.forEach((model) => {
    doc.setFontSize(9);
    doc.setTextColor(...mutedColor);
    doc.text(`${model.name}: ${model.accuracy}% accuracy`, margin + 5, y);
    y += 5;
  });
  
  y += 10;

  // Top Opportunities
  addSection('Top Opportunities');
  
  data.opportunities.forEach((opp, index) => {
    doc.setFontSize(10);
    doc.setTextColor(...textColor);
    doc.setFont('helvetica', 'bold');
    doc.text(`${index + 1}. ${opp.title}`, margin, y);
    
    doc.setTextColor(...successColor);
    doc.text(opp.impact, pageWidth - margin, y, { align: 'right' });
    y += 5;
    
    doc.setFontSize(9);
    doc.setTextColor(...mutedColor);
    doc.setFont('helvetica', 'normal');
    const descLines = doc.splitTextToSize(opp.description, contentWidth - 40);
    doc.text(descLines, margin + 5, y);
    y += descLines.length * 4 + 5;
  });

  // Footer
  y = doc.internal.pageSize.getHeight() - 15;
  doc.setDrawColor(...mutedColor);
  doc.setLineWidth(0.2);
  doc.line(margin, y - 5, pageWidth - margin, y - 5);
  
  doc.setFontSize(8);
  doc.setTextColor(...mutedColor);
  doc.text('Generated by PrismIQ Dynamic Pricing Intelligence Platform', margin, y);
  doc.text('Confidential', pageWidth - margin, y, { align: 'right' });

  // Save the PDF
  const filename = `PrismIQ_Executive_Report_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(filename);
}

