import { useCallback, useEffect, useState } from "react";

import { getJson } from "../api/client";
import type { HistoryItem } from "../api/types";

export function useHistory() {
  const [entries, setEntries] = useState<HistoryItem[]>([]);

  const refresh = useCallback(() => {
    getJson<HistoryItem[]>("/api/history")
      .then(setEntries)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { entries, refresh };
}
