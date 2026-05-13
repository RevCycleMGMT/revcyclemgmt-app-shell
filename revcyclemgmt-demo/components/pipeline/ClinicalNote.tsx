"use client";

import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type {
  ClinicalNoteSection,
  HighlightedPhrase,
  Scenario,
} from "@/lib/scenarios";

interface ClinicalNoteProps {
  scenario: Scenario;
  activeHighlightIndex?: number | null;
  revealedHighlightIndexes?: number[];
}

const sectionLabels: Record<string, string> = {
  cc: "CC",
  hpi: "HPI",
  pmhx: "PMHx",
  pe: "PE",
  ap: "A/P",
};

function renderMarkdownInline(text: string, keyPrefix: string): ReactNode[] {
  return text.split("\n").flatMap((line, lineIndex, lines) => {
    const parts = line.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    const nodes = parts.map((part, partIndex) => {
      const key = `${keyPrefix}-${lineIndex}-${partIndex}`;
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={key}>{part.slice(2, -2)}</strong>;
      }

      return <span key={key}>{part}</span>;
    });

    if (lineIndex < lines.length - 1) {
      nodes.push(<br key={`${keyPrefix}-${lineIndex}-br`} />);
    }

    return nodes;
  });
}

function renderSectionContent(
  section: ClinicalNoteSection,
  highlights: HighlightedPhrase[],
  activeHighlightIndex?: number | null,
  revealedHighlightIndexes: number[] = [],
  prefersReducedMotion = false
) {
  const sortedHighlights = highlights
    .map((highlight, highlightIndex) => ({ highlight, highlightIndex }))
    .filter(({ highlight }) => highlight.noteSectionId === section.id)
    .sort((a, b) => a.highlight.startOffset - b.highlight.startOffset);

  const nodes: ReactNode[] = [];
  let cursor = 0;

  sortedHighlights.forEach(({ highlight, highlightIndex }, index) => {
    const isActive = activeHighlightIndex === highlightIndex;
    const isRevealed = revealedHighlightIndexes.includes(highlightIndex);

    if (highlight.startOffset > cursor) {
      nodes.push(
        ...renderMarkdownInline(
          section.content.slice(cursor, highlight.startOffset),
          `${section.id}-plain-${index}`
        )
      );
    }

    nodes.push(
      <motion.span
        key={`${section.id}-highlight-${highlight.linksToCodeId}-${index}`}
        className="inline-block rounded-sm border-b border-teal-200 transition-colors duration-200 hover:cursor-help hover:bg-teal-50"
        animate={
          prefersReducedMotion
            ? {
                backgroundColor:
                  isActive || isRevealed
                    ? "rgb(240, 253, 250)"
                    : "rgba(240, 253, 250, 0)",
                scale: 1,
              }
            : isActive
            ? {
                backgroundColor: [
                  "rgba(240, 253, 250, 0)",
                  "rgb(204, 251, 241)",
                  "rgb(240, 253, 250)",
                ],
                scale: [1, 1.05, 1],
              }
            : {
                backgroundColor: isRevealed
                  ? "rgb(240, 253, 250)"
                  : "rgba(240, 253, 250, 0)",
                scale: 1,
              }
        }
        transition={
          prefersReducedMotion
            ? { duration: 0 }
            : isActive
            ? { duration: 0.5, ease: "easeInOut", times: [0, 0.5, 1] }
            : { duration: 0.2, ease: "easeOut" }
        }
        data-code-id={highlight.linksToCodeId}
        data-highlight-index={highlightIndex}
        data-note-section-id={highlight.noteSectionId}
        data-reveals={highlight.reveals}
      >
        {renderMarkdownInline(highlight.text, `${section.id}-highlight-text-${index}`)}
      </motion.span>
    );

    cursor = highlight.endOffset;
  });

  if (cursor < section.content.length) {
    nodes.push(
      ...renderMarkdownInline(
        section.content.slice(cursor),
        `${section.id}-plain-end`
      )
    );
  }

  return nodes;
}

export function ClinicalNote({
  scenario,
  activeHighlightIndex = null,
  revealedHighlightIndexes = [],
}: ClinicalNoteProps) {
  const prefersReducedMotion = Boolean(useReducedMotion());

  return (
    <Card className="rounded-xl border-slate-200 bg-white p-6 shadow-sm">
      <CardHeader className="p-0">
        <CardTitle className="text-xl font-semibold tracking-[0] text-slate-900">
          Clinical Note
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-8 p-0 pt-8">
        {scenario.encounter.note.map((section) => (
          <section key={section.id}>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500">
              {sectionLabels[section.id] ?? section.label}
            </h2>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
              {renderSectionContent(
                section,
                scenario.encounter.highlightedPhrases,
                activeHighlightIndex,
                revealedHighlightIndexes,
                prefersReducedMotion
              )}
            </p>
          </section>
        ))}
      </CardContent>
    </Card>
  );
}
