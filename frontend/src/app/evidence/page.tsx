'use client';

import { useState, useEffect } from 'react';
import { MasterLayout } from '@/components/layout';
import {
  DocNavigation,
  DocViewer,
  QuickReference,
} from '@/components/evidence';
import { getEvidence, getDocContent } from '@/services/evidenceService';
import type { EvidenceResponse } from '@/components/evidence/types';

export default function EvidencePage() {
  const [selectedDocId, setSelectedDocId] = useState('xgboost');
  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [docContent, setDocContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch evidence data on mount
  useEffect(() => {
    async function fetchEvidence() {
      try {
        const data = await getEvidence();
        setEvidence(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evidence');
      }
    }
    fetchEvidence();
  }, []);

  // Fetch document content when selection changes
  useEffect(() => {
    async function fetchDoc() {
      setIsLoading(true);
      try {
        const content = await getDocContent(selectedDocId);
        setDocContent(content);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document');
        setDocContent('');
      } finally {
        setIsLoading(false);
      }
    }
    fetchDoc();
  }, [selectedDocId]);

  const handleDocSelect = (docId: string) => {
    setSelectedDocId(docId);
  };

  return (
    <MasterLayout
      leftContent={
        <div className="p-4 h-full overflow-y-auto">
          <DocNavigation
            selectedId={selectedDocId}
            onSelect={handleDocSelect}
          />
        </div>
      }
      centerContent={
        <div className="flex-1 p-6 overflow-y-auto">
          {error && !isLoading ? (
            <div className="text-center text-destructive p-4">
              <p>{error}</p>
              <p className="text-sm text-muted-foreground mt-2">
                Make sure the backend is running and the evidence endpoint is available.
              </p>
            </div>
          ) : (
            <DocViewer content={docContent} isLoading={isLoading} />
          )}
        </div>
      }
      rightContent={
        <div className="p-4 h-full overflow-y-auto">
          <QuickReference
            evidence={evidence}
            selectedDocId={selectedDocId}
          />
        </div>
      }
    />
  );
}
