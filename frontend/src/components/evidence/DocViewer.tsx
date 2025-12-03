'use client';

import type { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import { Skeleton } from '@/components/ui/skeleton';

interface DocViewerProps {
  content: string;
  isLoading: boolean;
}

/**
 * Skeleton loader that mimics typical markdown document layout.
 * Displays realistic structure: H1 title, meta info, H2 sections,
 * paragraph text, tables, and code blocks.
 */
function DocumentSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* H1 Title */}
      <Skeleton className="h-9 w-2/3" />
      
      {/* Meta line (Version, Date, etc.) */}
      <div className="flex gap-4">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-20" />
      </div>
      
      {/* Horizontal rule */}
      <Skeleton className="h-px w-full" />
      
      {/* Section 1: Overview with paragraph */}
      <div className="space-y-3 pt-2">
        <Skeleton className="h-7 w-1/3" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-11/12" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </div>
      
      {/* Section 2: Details with bullet list */}
      <div className="space-y-3 pt-4">
        <Skeleton className="h-7 w-2/5" />
        <div className="space-y-2 pl-4">
          <div className="flex items-center gap-2">
            <Skeleton className="h-2 w-2 rounded-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-2 w-2 rounded-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-2 w-2 rounded-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        </div>
      </div>
      
      {/* Section 3: Table */}
      <div className="space-y-3 pt-4">
        <Skeleton className="h-7 w-1/4" />
        <div className="border rounded-lg overflow-hidden">
          {/* Table header */}
          <div className="flex gap-2 p-3 bg-muted/30">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-1/5" />
          </div>
          {/* Table rows */}
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex gap-2 p-3 border-t">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-1/5" />
            </div>
          ))}
        </div>
      </div>
      
      {/* Section 4: Code block */}
      <div className="space-y-3 pt-4">
        <Skeleton className="h-7 w-1/3" />
        <div className="bg-muted/50 rounded-lg p-4 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    </div>
  );
}

export const DocViewer: FC<DocViewerProps> = ({ content, isLoading }) => {
  if (isLoading) {
    return <DocumentSkeleton />;
  }

  if (!content) {
    return (
      <div className="text-center text-muted-foreground py-8">
        <p>Select a document from the navigation to view its contents.</p>
      </div>
    );
  }

  return (
    <article className="prose prose-slate dark:prose-invert max-w-none prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-sm prose-li:text-sm prose-table:text-sm">
      <ReactMarkdown
        components={{
          // Custom code block styling
          code({ className, children, ...props }) {
            const isInline = !className;
            return isInline ? (
              <code
                className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono"
                {...props}
              >
                {children}
              </code>
            ) : (
              <code
                className="block bg-muted p-4 rounded-lg text-sm font-mono overflow-x-auto"
                {...props}
              >
                {children}
              </code>
            );
          },
          // Style pre blocks
          pre({ children, ...props }) {
            return (
              <pre
                className="bg-muted p-4 rounded-lg overflow-x-auto"
                {...props}
              >
                {children}
              </pre>
            );
          },
          // Style tables
          table({ children, ...props }) {
            return (
              <div className="overflow-x-auto">
                <table
                  className="w-full border-collapse border border-border"
                  {...props}
                >
                  {children}
                </table>
              </div>
            );
          },
          th({ children, ...props }) {
            return (
              <th
                className="border border-border bg-muted px-4 py-2 text-left font-semibold"
                {...props}
              >
                {children}
              </th>
            );
          },
          td({ children, ...props }) {
            return (
              <td className="border border-border px-4 py-2" {...props}>
                {children}
              </td>
            );
          },
          // Style blockquotes
          blockquote({ children, ...props }) {
            return (
              <blockquote
                className="border-l-4 border-primary/50 pl-4 italic text-muted-foreground"
                {...props}
              >
                {children}
              </blockquote>
            );
          },
          // Style horizontal rules
          hr(props) {
            return <hr className="border-border my-8" {...props} />;
          },
          // Style links
          a({ href, children, ...props }) {
            return (
              <a
                href={href}
                className="text-primary hover:underline"
                target={href?.startsWith('http') ? '_blank' : undefined}
                rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
                {...props}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </article>
  );
};

