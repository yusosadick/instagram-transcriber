import { useJobContext } from "../context/JobContext";
import { CancelButton } from "./CancelButton";

const TERMINAL_STATUSES = new Set(["completed", "failed", "cancelled"]);

export function ProgressIndicator() {
  const { state } = useJobContext();
  if (!state.jobId || !state.status) return null;

  const isTerminal = TERMINAL_STATUSES.has(state.status);
  const isError = state.status === "failed";

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-soft dark:border-stone-700 dark:bg-stone-900">
      <div className="flex items-center justify-between">
        <span className={`text-sm font-medium ${isError ? "text-red-500" : "text-stone-700 dark:text-stone-200"}`}>
          {isError && state.error ? state.error.message : state.stageMessage}
        </span>
        {!isTerminal && <CancelButton />}
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-stone-100 dark:bg-stone-800">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isError ? "bg-red-400" : "bg-gradient-to-r from-orange-500 via-orange-400 to-amber-400"
          }`}
          style={{ width: `${state.progressPercent}%` }}
        />
      </div>
    </div>
  );
}
