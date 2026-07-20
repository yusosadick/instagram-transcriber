import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

import { postForm } from "../api/client";
import { useJobContext } from "../context/JobContext";
import type { JobResponse } from "../api/types";

export function FileDropZone() {
  const { dispatch } = useJobContext();
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (accepted: File[]) => {
      const file = accepted[0];
      if (!file) return;
      setError(null);
      const form = new FormData();
      form.append("file", file);
      try {
        const job = await postForm<JobResponse>("/api/jobs/upload", form);
        dispatch({ type: "START_JOB", jobId: job.id });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      }
    },
    [dispatch],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "audio/*": [], "video/*": [] },
    multiple: false,
  });

  return (
    <div className="flex flex-col gap-2">
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-xl border-2 border-dashed px-4 py-8 text-center text-sm shadow-soft transition ${
          isDragActive
            ? "border-brand-400 bg-brand-50 dark:bg-brand-900/20"
            : "border-stone-200 bg-white text-stone-500 hover:border-brand-300 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-400"
        }`}
      >
        <input {...getInputProps()} />
        <p>Drag &amp; drop an audio or video file here, or click to browse</p>
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
