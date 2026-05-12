"use client";

import { useState } from "react";
import { BookOpen, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface TeachingNotePanelProps {
  text: string;
}

export function TeachingNotePanel({ text }: TeachingNotePanelProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="fixed right-0 top-1/2 z-40 flex -translate-y-1/2 items-center">
      <button
        type="button"
        className={cn(
          "flex size-11 items-center justify-center rounded-l-lg border border-r-0 border-teal-200 bg-white text-teal-700 shadow-sm transition-colors duration-200 hover:bg-teal-50",
          isOpen && "border-teal-600 bg-teal-50"
        )}
        onClick={() => setIsOpen((value) => !value)}
        aria-label={isOpen ? "Close teaching note" : "Open teaching note"}
        aria-expanded={isOpen}
      >
        <BookOpen className="size-5" aria-hidden="true" />
      </button>

      <AnimatePresence>
        {isOpen ? (
          <motion.aside
            initial={{ x: 340, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 340, opacity: 0 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
            className="w-80 pr-4"
          >
            <Card className="rounded-r-none border-l-4 border-l-teal-600 border-slate-200 bg-teal-50 p-5 shadow-md">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-sm font-semibold text-teal-700">
                  Teaching Note
                </h2>
                <button
                  type="button"
                  className="rounded-md p-1 text-slate-500 transition-colors duration-200 hover:bg-white hover:text-slate-900"
                  onClick={() => setIsOpen(false)}
                  aria-label="Close teaching note"
                >
                  <X className="size-4" aria-hidden="true" />
                </button>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-700">{text}</p>
            </Card>
          </motion.aside>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
