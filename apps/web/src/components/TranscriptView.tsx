import { useState, type ReactNode } from "react";

import type { TranscriptResult } from "../api/types";
import { CopyButton } from "./CopyButton";
import { ExportMenu } from "./ExportMenu";

function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function TranscriptView({ jobId, result }: { jobId: string; result: TranscriptResult }) {
  const [showTimestamps, setShowTimestamps] = useState(true);

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-stone-200 bg-white p-6 shadow-soft dark:border-stone-700 dark:bg-stone-900">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <Badge>{result.language.toUpperCase()} ({Math.round(result.language_probability * 100)}%)</Badge>
        <Badge>{formatTimestamp(result.duration)}</Badge>
        <Badge>{result.word_count} words</Badge>
        <Badge>{result.model_size} · {result.device}</Badge>
        <label className="ml-auto flex items-center gap-2 text-stone-500 dark:text-stone-400">
          <input
            type="checkbox"
            checked={showTimestamps}
            onChange={(e) => setShowTimestamps(e.target.checked)}
            className="accent-orange-500"
          />
          Timestamps
        </label>
      </div>

      <div className="max-h-96 space-y-2 overflow-y-auto pr-1 text-sm leading-relaxed text-stone-700 dark:text-stone-200">
        {result.segments.map((seg, i) => (
          <p key={i}>
            {showTimestamps && (
              <span className="mr-2 font-mono text-xs text-brand-500">[{formatTimestamp(seg.start)}]</span>
            )}
            {seg.text}
          </p>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-stone-100 pt-4 dark:border-stone-800">
        <CopyButton text={result.text} />
        <ExportMenu jobId={jobId} />
      </div>
    </div>
  );
}

function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-full bg-stone-100 px-2.5 py-1 font-medium text-stone-600 dark:bg-stone-800 dark:text-stone-300">
      {children}
    </span>
  );
}
