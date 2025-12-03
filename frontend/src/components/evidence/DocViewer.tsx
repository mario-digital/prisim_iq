'use client';

import type { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import { Skeleton } from '@/components/ui/skeleton';

interface DocViewerProps {
  content: string;
  isLoading: boolean;
}

function DocumentSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="pt-4 space-y-3">
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-3/4" />
      </div>
      <div className="pt-4 space-y-3">
        <Skeleton className="h-6 w-2/5" />
        <Skeleton className="h-32 w-full" />
      </div>
      <div className="pt-4 space-y-3">
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
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

