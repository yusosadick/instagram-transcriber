import { useEffect } from "react";

import { useJobContext } from "../context/JobContext";
import { useHistory } from "../hooks/useHistory";

export function HistoryList() {
  const { entries, refresh } = useHistory();
  const { state } = useJobContext();

  useEffect(() => {
    if (state.status === "completed") refresh();
  }, [state.status, refresh]);

  if (entries.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-semibold text-stone-500 dark:text-stone-400">Recent</h2>
      <ul className="flex flex-col gap-2">
        {entries.map((entry) => (
          <li
            key={entry.id}
            className="flex items-center justify-between rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm shadow-soft dark:border-stone-700 dark:bg-stone-900"
          >
            <div className="min-w-0">
              <p className="truncate font-medium text-stone-700 dark:text-stone-200">{entry.title}</p>
              <p className="truncate text-xs text-stone-400">{entry.source}</p>
            </div>
            <span className="ml-3 shrink-0 text-xs text-stone-400">{entry.word_count} words</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
