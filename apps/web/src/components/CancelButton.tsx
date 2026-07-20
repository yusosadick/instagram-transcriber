import { useState } from "react";

import { postJson } from "../api/client";
import { useJobContext } from "../context/JobContext";

export function CancelButton() {
  const { state } = useJobContext();
  const [cancelling, setCancelling] = useState(false);

  const handleCancel = async () => {
    if (!state.jobId) return;
    setCancelling(true);
    try {
      await postJson(`/api/jobs/${state.jobId}/cancel`, {});
    } catch {
      // job may have already reached a terminal state — polling will reflect it
    }
  };

  return (
    <button
      type="button"
      onClick={handleCancel}
      disabled={cancelling}
      className="rounded-xl border border-stone-200 px-3 py-1.5 text-xs font-medium text-stone-600 transition hover:bg-stone-50 disabled:opacity-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
    >
      {cancelling ? "Cancelling..." : "Cancel"}
    </button>
  );
}
