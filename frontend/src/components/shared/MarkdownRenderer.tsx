"use client";

import { cn } from "@/lib/utils/cn";

/**
 * Simple markdown-to-JSX renderer.
 * Handles: ## headings, **bold**, - bullet items, plain paragraphs, line breaks.
 */
export function MarkdownRenderer({ text, className }: { text: string; className?: string }) {
  if (!text) return null;

  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Empty line = paragraph break
    if (line.trim() === "") {
      elements.push(<div key={key++} className="h-3" />);
      i++;
      continue;
    }

    // ## Heading
    if (line.match(/^##\s+/)) {
      const content = line.replace(/^##\s+/, "");
      elements.push(
        <h3 key={key++} className="text-base font-semibold text-slate-900 dark:text-white mt-4 mb-2">
          {renderInlineMarkdown(content)}
        </h3>
      );
      i++;
      continue;
    }

    // ### Sub-heading
    if (line.match(/^###\s+/)) {
      const content = line.replace(/^###\s+/, "");
      elements.push(
        <h4 key={key++} className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-3 mb-1">
          {renderInlineMarkdown(content)}
        </h4>
      );
      i++;
      continue;
    }

    // Bullet point (- or *)
    if (line.match(/^[\-\*]\s+/)) {
      const items: React.ReactNode[] = [];
      while (i < lines.length && lines[i].match(/^[\-\*]\s+/)) {
        const content = lines[i].replace(/^[\-\*]\s+/, "");
        items.push(
          <li key={key++} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300 ml-2 mb-1">
            <span className="mt-1.5 h-1 w-1 rounded-full bg-slate-400 flex-shrink-0" />
            <span>{renderInlineMarkdown(content)}</span>
          </li>
        );
        i++;
      }
      elements.push(<ul key={key++} className="space-y-0.5 mb-2">{items}</ul>);
      continue;
    }

    // Numbered list
    if (line.match(/^\d+\.\s+/)) {
      const items: React.ReactNode[] = [];
      while (i < lines.length && lines[i].match(/^\d+\.\s+/)) {
        const content = lines[i].replace(/^\d+\.\s+/, "");
        const num = lines[i].match(/^(\d+)\./)?.[1] || "";
        items.push(
          <li key={key++} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300 ml-2 mb-1">
            <span className="text-slate-400 font-mono text-xs w-4 flex-shrink-0 mt-0.5">{num}.</span>
            <span>{renderInlineMarkdown(content)}</span>
          </li>
        );
        i++;
      }
      elements.push(<ol key={key++} className="space-y-0.5 mb-2">{items}</ol>);
      continue;
    }

    // Horizontal rule
    if (line.match(/^---/)) {
      elements.push(<hr key={key++} className="my-3 border-slate-200 dark:border-slate-700" />);
      i++;
      continue;
    }

    // Regular paragraph
    const paragraphLines: string[] = [];
    while (i < lines.length && lines[i].trim() !== "" && !lines[i].match(/^(##|###|[\-\*\d])/)) {
      paragraphLines.push(lines[i]);
      i++;
    }
    if (paragraphLines.length > 0) {
      const text = paragraphLines.join(" ");
      elements.push(
        <p key={key++} className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-2">
          {renderInlineMarkdown(text)}
        </p>
      );
    }
  }

  return <div className={cn("", className)}>{elements}</div>;
}

/** Render inline **bold** within a text fragment */
function renderInlineMarkdown(text: string): React.ReactNode {
  // Split on **bold** markers
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-slate-800 dark:text-slate-200">
          {part.slice(2, -2)}
        </strong>
      );
    }
    // Handle *italic*
    const italicParts = part.split(/(\*[^*]+\*)/g);
    if (italicParts.length > 1) {
      return italicParts.map((ip, j) => {
        if (ip.startsWith("*") && ip.endsWith("*")) {
          return <em key={`${i}-${j}`} className="italic">{ip.slice(1, -1)}</em>;
        }
        return ip;
      });
    }
    return part;
  });
}
