import { useState } from "react";

import { postJson } from "../api/client";
import { useJobContext } from "../context/JobContext";
import { isInstagramUrl } from "../lib/validateInstagramUrl";
import type { JobResponse } from "../api/types";

export function UrlInputForm() {
  const { dispatch } = useJobContext();
  const [url, setUrl] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setUrl(text);
      setValidationError(null);
    } catch {
      // clipboard read blocked (permissions/insecure context) — user can paste manually
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isInstagramUrl(url)) {
      setValidationError("Not a valid Instagram Reel/Post URL");
      return;
    }
    setValidationError(null);
    setSubmitting(true);
    try {
      const job = await postJson<JobResponse>("/api/jobs", { url });
      dispatch({ type: "START_JOB", jobId: job.id });
    } catch (err) {
      setValidationError(err instanceof Error ? err.message : "Could not start job");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.instagram.com/reel/..."
          className="flex-1 rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm shadow-soft outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-200 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100"
        />
        <button
          type="button"
          onClick={handlePaste}
          className="rounded-xl border border-stone-200 px-4 py-3 text-sm font-medium text-stone-600 shadow-soft transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
        >
          Paste
        </button>
      </div>
      {validationError && <p className="text-sm text-red-500">{validationError}</p>}
      <button
        type="submit"
        disabled={submitting || !url}
        className="rounded-xl bg-gradient-to-br from-orange-500 via-orange-400 to-amber-400 px-4 py-3 text-sm font-semibold text-white shadow-soft transition hover:shadow-glow disabled:cursor-not-allowed disabled:opacity-50"
      >
        {submitting ? "Starting..." : "Transcribe"}
      </button>
    </form>
  );
}
