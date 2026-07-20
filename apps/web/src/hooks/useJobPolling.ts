import { useEffect } from "react";

import { getJson } from "../api/client";
import type { JobStatusResponse, TranscriptResult } from "../api/types";
import { useJobContext } from "../context/JobContext";

const POLL_INTERVAL_MS = 1500;
const TERMINAL_STATUSES = new Set(["completed", "failed", "cancelled"]);

export function useJobPolling() {
  const { state, dispatch } = useJobContext();
  const { jobId } = state;

  // Keyed only on jobId (not status): re-running this effect on every status
  // change would tear down the in-flight poll() closure right as a job hits
  // "completed", dropping the result fetch that happens later in the same
  // call. The poll loop below decides on its own when to stop.
  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const job = await getJson<JobStatusResponse>(`/api/jobs/${jobId}`);
        if (cancelled) return;
        dispatch({
          type: "UPDATE_STATUS",
          status: job.status,
          stageMessage: job.stage_message,
          progressPercent: job.progress_percent,
          error: job.error,
        });

        if (job.status === "completed") {
          const result = await getJson<TranscriptResult>(`/api/jobs/${jobId}/result`);
          if (!cancelled) dispatch({ type: "SET_RESULT", result });
        }

        if (!cancelled && !TERMINAL_STATUSES.has(job.status)) {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch {
        if (!cancelled) timer = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [jobId, dispatch]);
}
