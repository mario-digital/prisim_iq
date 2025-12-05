import { jsPDF } from 'jspdf';
import { fallbackMapping, type HoneywellMappingData } from './MappingTable';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function generateHoneywellPDF(): Promise<void> {
  // Try to fetch latest mapping data, fall back to static data
  let mappingData: HoneywellMappingData = fallbackMapping;

  try {
    const response = await fetch(`${API_BASE}/api/v1/honeywell_mapping`);
    if (response.ok) {
      const data = await response.json();
      mappingData = {
        title: 'Ride-Sharing to Honeywell Enterprise Mapping',
        description:
          'How dynamic pricing concepts translate to enterprise applications',
        mappings: Object.entries(data.mapping || {}).map(([key, value]) => ({
          ride_sharing_concept: key,
          honeywell_equivalent: String(value),
          rationale:
            fallbackMapping.mappings.find((m) => m.ride_sharing_concept === key)
              ?.rationale || 'Enterprise application of the concept.',
        })),
        compliance_notes: data.compliance_notes || fallbackMapping.compliance_notes,
      };
    }
  } catch {
    console.warn('Using fallback mapping data for PDF');
  }

  const pdf = new jsPDF('p', 'pt', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 40;
  let yPos = margin;

  // Helper functions
  const addText = (
    text: string,
    x: number,
    y: number,
    options?: {
      fontSize?: number;
      fontStyle?: 'normal' | 'bold' | 'italic';
      color?: [number, number, number];
      maxWidth?: number;
    }
  ) => {
    const { fontSize = 10, fontStyle = 'normal', color = [51, 51, 51], maxWidth } = options || {};
    pdf.setFontSize(fontSize);
    pdf.setFont('helvetica', fontStyle);
    pdf.setTextColor(...color);
    if (maxWidth) {
      pdf.text(text, x, y, { maxWidth });
    } else {
      pdf.text(text, x, y);
    }
  };

  const addLine = (y: number, color: [number, number, number] = [200, 200, 200]) => {
    pdf.setDrawColor(...color);
    pdf.setLineWidth(0.5);
    pdf.line(margin, y, pageWidth - margin, y);
  };

  const checkPageBreak = (requiredSpace: number) => {
    if (yPos + requiredSpace > pageHeight - margin) {
      pdf.addPage();
      yPos = margin;
      return true;
    }
    return false;
  };

  // Header
  addText('PrismIQ', margin, yPos, { fontSize: 24, fontStyle: 'bold', color: [59, 130, 246] });
  yPos += 25;
  addText('Ride-Sharing to Honeywell Enterprise Mapping', margin, yPos, {
    fontSize: 16,
    fontStyle: 'bold',
  });
  yPos += 20;
  addText(`Generated: ${new Date().toLocaleDateString()}`, margin, yPos, {
    fontSize: 9,
    color: [128, 128, 128],
  });
  yPos += 30;
  addLine(yPos);
  yPos += 20;

  // Introduction
  addText('Executive Summary', margin, yPos, { fontSize: 14, fontStyle: 'bold' });
  yPos += 20;
  const introText =
    'This document demonstrates how PrismIQ\'s dynamic pricing algorithms and methodologies ' +
    'translate directly to Honeywell\'s enterprise manufacturing and supply chain applications. ' +
    'The underlying AI models and business logic are domain-agnostic, providing immediate value ' +
    'across industries.';
  addText(introText, margin, yPos, { fontSize: 10, maxWidth: pageWidth - 2 * margin });
  yPos += 60;

  // Mapping Table Header
  addLine(yPos);
  yPos += 15;
  addText('Concept Mapping Table', margin, yPos, { fontSize: 14, fontStyle: 'bold' });
  yPos += 25;

  // Table headers
  const col1Width = 150;
  const col2Width = 150;
  const col3Width = pageWidth - 2 * margin - col1Width - col2Width - 20;

  pdf.setFillColor(245, 245, 245);
  pdf.rect(margin, yPos - 5, pageWidth - 2 * margin, 25, 'F');
  addText('Ride-Sharing', margin + 5, yPos + 10, { fontSize: 9, fontStyle: 'bold' });
  addText('Honeywell', margin + col1Width + 10, yPos + 10, { fontSize: 9, fontStyle: 'bold' });
  addText('Business Rationale', margin + col1Width + col2Width + 15, yPos + 10, {
    fontSize: 9,
    fontStyle: 'bold',
  });
  yPos += 30;

  // Table rows
  for (const row of mappingData.mappings) {
    checkPageBreak(60);

    // Row background alternating
    const rowIndex = mappingData.mappings.indexOf(row);
    if (rowIndex % 2 === 1) {
      pdf.setFillColor(250, 250, 250);
      pdf.rect(margin, yPos - 5, pageWidth - 2 * margin, 45, 'F');
    }

    // Ride-sharing concept
    addText(row.ride_sharing_concept, margin + 5, yPos + 5, {
      fontSize: 9,
      fontStyle: 'bold',
      color: [59, 130, 246],
    });

    // Arrow
    addText('→', margin + col1Width - 10, yPos + 5, {
      fontSize: 12,
      color: [128, 128, 128],
    });

    // Honeywell equivalent
    addText(row.honeywell_equivalent, margin + col1Width + 10, yPos + 5, {
      fontSize: 9,
      fontStyle: 'bold',
      color: [234, 88, 12],
    });

    // Rationale (wrapped)
    const rationaleLines = pdf.splitTextToSize(row.rationale, col3Width - 10);
    addText(rationaleLines.slice(0, 2).join('\n'), margin + col1Width + col2Width + 15, yPos + 5, {
      fontSize: 8,
      color: [100, 100, 100],
    });

    yPos += 50;
    addLine(yPos - 5, [230, 230, 230]);
  }

  // Compliance section
  checkPageBreak(120);
  yPos += 20;
  addText('Compliance & Governance', margin, yPos, { fontSize: 14, fontStyle: 'bold' });
  yPos += 20;

  for (const note of mappingData.compliance_notes) {
    checkPageBreak(20);
    addText(`✓ ${note}`, margin + 10, yPos, { fontSize: 9, color: [34, 139, 34] });
    yPos += 15;
  }

  // Footer on each page
  const totalPages = pdf.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.setTextColor(128, 128, 128);
    pdf.text('Confidential - PrismIQ', margin, pageHeight - 20);
    pdf.text(`Page ${i} of ${totalPages}`, pageWidth - margin - 50, pageHeight - 20);
  }

  // Save the PDF
  pdf.save(`PrismIQ_Honeywell_Mapping_${new Date().toISOString().split('T')[0]}.pdf`);
}

