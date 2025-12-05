import { jsPDF } from 'jspdf';
import { fallbackMapping, type HoneywellMappingData } from './MappingTable';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function generateHoneywellPDF(): Promise<void> {
  // Use the rich fallback data (which has all the context from the kickoff)
  const mappingData: HoneywellMappingData = fallbackMapping;

  const pdf = new jsPDF('p', 'pt', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 40;
  const contentWidth = pageWidth - 2 * margin;
  let yPos = margin;

  // Colors
  const primaryColor: [number, number, number] = [59, 130, 246]; // Blue
  const honeywellOrange: [number, number, number] = [234, 88, 12];
  const textDark: [number, number, number] = [30, 30, 30];
  const textMuted: [number, number, number] = [100, 100, 100];
  const greenColor: [number, number, number] = [34, 139, 34];

  // Helper functions
  const setFont = (size: number, style: 'normal' | 'bold' = 'normal', color: [number, number, number] = textDark) => {
    pdf.setFontSize(size);
    pdf.setFont('helvetica', style);
    pdf.setTextColor(...color);
  };

  const addLine = (y: number, color: [number, number, number] = [220, 220, 220]) => {
    pdf.setDrawColor(...color);
    pdf.setLineWidth(0.5);
    pdf.line(margin, y, pageWidth - margin, y);
  };

  const checkPageBreak = (requiredSpace: number): boolean => {
    if (yPos + requiredSpace > pageHeight - 60) {
      pdf.addPage();
      yPos = margin;
      return true;
    }
    return false;
  };

  const wrapText = (text: string, maxWidth: number): string[] => {
    return pdf.splitTextToSize(text, maxWidth);
  };

  // =========================================================================
  // PAGE 1: Cover & Executive Summary
  // =========================================================================
  
  // Header
  setFont(28, 'bold', primaryColor);
  pdf.text('PrismIQ', margin, yPos + 10);
  
  setFont(10, 'normal', textMuted);
  pdf.text('AI-Powered Dynamic Pricing', margin + 85, yPos + 10);
  
  yPos += 40;
  
  // Title
  setFont(20, 'bold', textDark);
  pdf.text('Ride-Sharing to Honeywell Aerospace', margin, yPos);
  yPos += 22;
  setFont(20, 'bold', honeywellOrange);
  pdf.text('Enterprise Mapping', margin, yPos);
  yPos += 30;
  
  // Metadata
  setFont(10, 'normal', textMuted);
  pdf.text(`Generated: ${new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })}`, margin, yPos);
  yPos += 15;
  pdf.text('Confidential - For Honeywell Hackathon Evaluation', margin, yPos);
  yPos += 25;
  
  addLine(yPos);
  yPos += 25;

  // Executive Summary
  setFont(14, 'bold', textDark);
  pdf.text('Executive Summary', margin, yPos);
  yPos += 18;
  
  setFont(10, 'normal', textDark);
  const summaryText = `This document demonstrates how PrismIQ's dynamic pricing algorithms and methodologies 
translate directly to Honeywell Aerospace's aftermarket business. The same AI models that optimize 
ride-sharing pricing can optimize aerospace parts pricing, expedite fees, and customer segmentation 
for airlines like Emirates, Delta, and Southwest Airlines.`;
  
  const summaryLines = wrapText(summaryText, contentWidth);
  pdf.text(summaryLines, margin, yPos);
  yPos += summaryLines.length * 14 + 20;

  // Honeywell Context Box
  pdf.setFillColor(255, 247, 237); // Light orange background
  pdf.roundedRect(margin, yPos, contentWidth, 85, 5, 5, 'F');
  pdf.setDrawColor(...honeywellOrange);
  pdf.setLineWidth(1);
  pdf.roundedRect(margin, yPos, contentWidth, 85, 5, 5, 'S');
  
  yPos += 15;
  setFont(11, 'bold', honeywellOrange);
  pdf.text('🏭 Honeywell Aerospace Context', margin + 10, yPos);
  yPos += 15;
  
  setFont(9, 'normal', textDark);
  const contextLines = wrapText(mappingData.context, contentWidth - 20);
  pdf.text(contextLines.slice(0, 5), margin + 10, yPos);
  yPos += 75;

  // =========================================================================
  // PAGE 2: Concept Mapping Table
  // =========================================================================
  pdf.addPage();
  yPos = margin;

  setFont(16, 'bold', textDark);
  pdf.text('Concept Mapping Table', margin, yPos);
  yPos += 25;

  // Table header
  const col1X = margin;
  const col2X = margin + 160;
  const col3X = margin + 340;
  const col1W = 155;
  const col2W = 175;
  const col3W = contentWidth - col1W - col2W - 10;

  pdf.setFillColor(240, 240, 240);
  pdf.rect(margin, yPos - 5, contentWidth, 22, 'F');
  
  setFont(8, 'bold', textMuted);
  pdf.text('RIDE-SHARING CONCEPT', col1X + 5, yPos + 8);
  pdf.text('HONEYWELL AEROSPACE', col2X + 5, yPos + 8);
  pdf.text('BUSINESS RATIONALE', col3X + 5, yPos + 8);
  yPos += 25;
  addLine(yPos - 5, [200, 200, 200]);

  // Table rows
  for (let i = 0; i < mappingData.mappings.length; i++) {
    const row = mappingData.mappings[i];
    
    checkPageBreak(70);

    // Alternating row background
    if (i % 2 === 1) {
      pdf.setFillColor(250, 250, 250);
      pdf.rect(margin, yPos - 3, contentWidth, 60, 'F');
    }

    // Ride-sharing concept (cyan)
    setFont(9, 'bold', primaryColor);
    const concept = wrapText(row.ride_sharing_concept, col1W - 10);
    pdf.text(concept, col1X + 5, yPos + 8);

    // Arrow
    setFont(12, 'normal', textMuted);
    pdf.text('→', col2X - 15, yPos + 12);

    // Honeywell equivalent (orange)
    setFont(9, 'bold', honeywellOrange);
    const equivalent = wrapText(row.honeywell_equivalent, col2W - 10);
    pdf.text(equivalent, col2X + 5, yPos + 8);

    // Rationale
    setFont(8, 'normal', textMuted);
    const rationale = wrapText(row.rationale, col3W - 5);
    pdf.text(rationale.slice(0, 4), col3X + 5, yPos + 8);

    yPos += 65;
    addLine(yPos - 5, [230, 230, 230]);
  }

  // =========================================================================
  // PAGE 3: Business Value & Compliance
  // =========================================================================
  pdf.addPage();
  yPos = margin;

  // Business Value Section
  setFont(14, 'bold', greenColor);
  pdf.text('📈 Business Value for Honeywell', margin, yPos);
  yPos += 20;

  pdf.setFillColor(240, 253, 244); // Light green background
  pdf.roundedRect(margin, yPos, contentWidth, 90, 5, 5, 'F');
  pdf.setDrawColor(...greenColor);
  pdf.setLineWidth(0.5);
  pdf.roundedRect(margin, yPos, contentWidth, 90, 5, 5, 'S');
  
  yPos += 15;
  setFont(9, 'normal', textDark);
  
  for (let i = 0; i < mappingData.business_value.length; i++) {
    const value = mappingData.business_value[i];
    pdf.setTextColor(...greenColor);
    pdf.text('●', margin + 10, yPos);
    pdf.setTextColor(...textDark);
    pdf.text(value, margin + 22, yPos);
    yPos += 14;
  }
  
  yPos += 30;

  // Compliance Section
  setFont(14, 'bold', primaryColor);
  pdf.text('🛡️ Compliance & Governance', margin, yPos);
  yPos += 20;

  pdf.setFillColor(245, 245, 245);
  pdf.roundedRect(margin, yPos, contentWidth, 85, 5, 5, 'F');
  
  yPos += 15;
  setFont(9, 'normal', textDark);
  
  for (let i = 0; i < mappingData.compliance_notes.length; i++) {
    const note = mappingData.compliance_notes[i];
    pdf.setTextColor(...greenColor);
    pdf.text('✓', margin + 10, yPos);
    pdf.setTextColor(...textDark);
    const noteLines = wrapText(note, contentWidth - 30);
    pdf.text(noteLines[0], margin + 22, yPos);
    yPos += 14;
  }

  yPos += 40;

  // Key Takeaway Box
  pdf.setFillColor(239, 246, 255); // Light blue background
  pdf.roundedRect(margin, yPos, contentWidth, 70, 5, 5, 'F');
  pdf.setDrawColor(...primaryColor);
  pdf.setLineWidth(1);
  pdf.roundedRect(margin, yPos, contentWidth, 70, 5, 5, 'S');
  
  yPos += 15;
  setFont(11, 'bold', primaryColor);
  pdf.text('💡 Key Takeaway', margin + 10, yPos);
  yPos += 15;
  
  setFont(9, 'normal', textDark);
  const takeawayText = `PrismIQ's AI-powered dynamic pricing is domain-agnostic. The same algorithms optimizing 
ride-sharing can immediately add value to Honeywell's $2B+ aerospace aftermarket business—improving 
revenue, reducing AOG response time, and enhancing channel partner relationships.`;
  const takeawayLines = wrapText(takeawayText, contentWidth - 20);
  pdf.text(takeawayLines, margin + 10, yPos);

  // =========================================================================
  // Footer on each page
  // =========================================================================
  const totalPages = pdf.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.setTextColor(128, 128, 128);
    pdf.text('Confidential - PrismIQ Hackathon Submission', margin, pageHeight - 25);
    pdf.text(`Page ${i} of ${totalPages}`, pageWidth - margin - 50, pageHeight - 25);
    
    // Add Honeywell + PrismIQ logos placeholder
    pdf.setDrawColor(200, 200, 200);
    pdf.line(margin, pageHeight - 35, pageWidth - margin, pageHeight - 35);
  }

  // Save the PDF
  pdf.save(`PrismIQ_Honeywell_Mapping_${new Date().toISOString().split('T')[0]}.pdf`);
}
