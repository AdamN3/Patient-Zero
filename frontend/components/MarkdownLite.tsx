"use client";

import type { ReactNode } from "react";

/**
 * Minimal renderer for the assessor's markdown-ish output: bullet lists,
 * numbered lists, paragraphs and **bold** spans. No external libraries,
 * no raw HTML injection.
 */

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={`${keyPrefix}-b${index}`} className="font-semibold text-[#0a2540]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <span key={`${keyPrefix}-t${index}`}>{part}</span>;
  });
}

type Block =
  | { kind: "ul"; items: string[] }
  | { kind: "ol"; items: string[] }
  | { kind: "p"; text: string };

function toBlocks(markdown: string): Block[] {
  const blocks: Block[] = [];
  let paragraph: string[] = [];

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push({ kind: "p", text: paragraph.join(" ") });
      paragraph = [];
    }
  };

  for (const rawLine of markdown.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      continue;
    }

    const bullet = line.match(/^[-*•]\s+(.*)$/);
    const numbered = line.match(/^\d+[.)]\s+(.*)$/);

    if (bullet) {
      flushParagraph();
      const last = blocks[blocks.length - 1];
      if (last?.kind === "ul") last.items.push(bullet[1]);
      else blocks.push({ kind: "ul", items: [bullet[1]] });
      continue;
    }

    if (numbered) {
      flushParagraph();
      const last = blocks[blocks.length - 1];
      if (last?.kind === "ol") last.items.push(numbered[1]);
      else blocks.push({ kind: "ol", items: [numbered[1]] });
      continue;
    }

    // Sub-heading-ish line inside a section (e.g. "### Pain characterisation").
    const heading = line.replace(/^#+\s*/, "");
    if (heading !== line) {
      flushParagraph();
      blocks.push({ kind: "p", text: `**${heading}**` });
      continue;
    }

    paragraph.push(line);
  }

  flushParagraph();
  return blocks;
}

interface MarkdownLiteProps {
  text: string;
  className?: string;
  emptyText?: string;
}

export default function MarkdownLite({
  text,
  className = "",
  emptyText = "—",
}: MarkdownLiteProps) {
  const blocks = toBlocks(text);

  if (!blocks.length) {
    return <p className={`text-slate-400 ${className}`}>{emptyText}</p>;
  }

  return (
    <div className={`space-y-3 text-sm leading-relaxed text-[#425466] ${className}`}>
      {blocks.map((block, blockIndex) => {
        const key = `blk-${blockIndex}`;
        if (block.kind === "p") {
          return <p key={key}>{renderInline(block.text, key)}</p>;
        }
        if (block.kind === "ul") {
          return (
            <ul key={key} className="list-disc space-y-1.5 pl-5 marker:text-[#635bff]">
              {block.items.map((item, itemIndex) => (
                <li key={`${key}-${itemIndex}`}>{renderInline(item, `${key}-${itemIndex}`)}</li>
              ))}
            </ul>
          );
        }
        return (
          <ol key={key} className="list-decimal space-y-1.5 pl-5 marker:font-semibold marker:text-[#635bff]">
            {block.items.map((item, itemIndex) => (
              <li key={`${key}-${itemIndex}`}>{renderInline(item, `${key}-${itemIndex}`)}</li>
            ))}
          </ol>
        );
      })}
    </div>
  );
}
