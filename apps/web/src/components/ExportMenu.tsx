import { downloadFileUrl } from "../api/client";
import type { ExportFormat } from "../api/types";

const FORMATS: { fmt: ExportFormat; label: string }[] = [
  { fmt: "txt", label: "Download TXT" },
  { fmt: "srt", label: "Download SRT" },
  { fmt: "json", label: "Download JSON" },
];

export function ExportMenu({ jobId }: { jobId: string }) {
  return (
    <div className="flex flex-wrap gap-2">
      {FORMATS.map(({ fmt, label }) => (
        <a
          key={fmt}
          href={downloadFileUrl(`/api/jobs/${jobId}/download/${fmt}`)}
          download
          className="rounded-xl border border-stone-200 px-4 py-2 text-sm font-medium text-stone-600 shadow-soft transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
        >
          {label}
        </a>
      ))}
    </div>
  );
}
