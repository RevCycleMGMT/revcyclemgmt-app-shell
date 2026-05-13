"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface X12EdiDisplayProps {
  edi: string;
}

function getParserReadyEdi(edi: string) {
  return edi
    .split("\n")
    .filter((line) => !line.trimStart().startsWith("//"))
    .join("\n");
}

function HighlightedEdiLine({ line }: { line: string }) {
  if (line.startsWith("//")) {
    return <div className="italic text-slate-500">{line}</div>;
  }

  const parts = line.split(/(\*|~)/);
  let hasRenderedSegmentId = false;

  return (
    <div>
      {parts.map((part, index) => {
        if (part === "*") {
          return (
            <span key={`${part}-${index}`} className="text-slate-500">
              *
            </span>
          );
        }

        if (part === "~") {
          return (
            <span key={`${part}-${index}`} className="text-rose-400">
              ~
            </span>
          );
        }

        if (!hasRenderedSegmentId && part.length > 0) {
          hasRenderedSegmentId = true;
          return (
            <span key={`${part}-${index}`} className="font-semibold text-teal-400">
              {part}
            </span>
          );
        }

        return <span key={`${part}-${index}`}>{part}</span>;
      })}
    </div>
  );
}

export function X12EdiDisplay({ edi }: X12EdiDisplayProps) {
  const [copied, setCopied] = useState(false);

  const copyEdi = async () => {
    const parserReadyEdi = getParserReadyEdi(edi);
    const fallbackCopy = () => {
      const textarea = document.createElement("textarea");

      textarea.value = parserReadyEdi;
      textarea.setAttribute("readonly", "true");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    };

    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(parserReadyEdi);
      } else {
        fallbackCopy();
      }
    } catch {
      fallbackCopy();
    }

    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  return (
    <Card className="overflow-hidden rounded-xl border-slate-800 bg-slate-900 p-0 text-slate-50 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-400">
            X12 837P
          </p>
          <h2 className="mt-1 text-sm font-semibold text-slate-100">
            Professional Claim EDI
          </h2>
        </div>
        <Button
          type="button"
          variant="outline"
          className="rounded-lg border-slate-700 bg-slate-800 text-slate-50 hover:bg-slate-700 hover:text-white"
          onClick={copyEdi}
        >
          {copied ? (
            <Check className="size-4" aria-hidden="true" />
          ) : (
            <Copy className="size-4" aria-hidden="true" />
          )}
          {copied ? "Copied" : "Copy EDI"}
        </Button>
      </div>
      <div className="overflow-x-auto p-8 font-mono text-sm leading-6">
        {edi.split("\n").map((line, index) => (
          <HighlightedEdiLine key={`${line}-${index}`} line={line} />
        ))}
      </div>
    </Card>
  );
}
