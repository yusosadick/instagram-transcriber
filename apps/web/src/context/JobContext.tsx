import { createContext, useContext, useReducer, type Dispatch, type ReactNode } from "react";

import type { JobError, JobStatus, TranscriptResult } from "../api/types";

export interface JobState {
  jobId: string | null;
  status: JobStatus | null;
  stageMessage: string;
  progressPercent: number;
  result: TranscriptResult | null;
  error: JobError | null;
}

type JobAction =
  | { type: "START_JOB"; jobId: string }
  | { type: "UPDATE_STATUS"; status: JobStatus; stageMessage: string; progressPercent: number; error: JobError | null }
  | { type: "SET_RESULT"; result: TranscriptResult }
  | { type: "RESET" };

const initialState: JobState = {
  jobId: null,
  status: null,
  stageMessage: "",
  progressPercent: 0,
  result: null,
  error: null,
};

function reducer(state: JobState, action: JobAction): JobState {
  switch (action.type) {
    case "START_JOB":
      return { ...initialState, jobId: action.jobId, status: "queued" };
    case "UPDATE_STATUS":
      return {
        ...state,
        status: action.status,
        stageMessage: action.stageMessage,
        progressPercent: action.progressPercent,
        error: action.error,
      };
    case "SET_RESULT":
      return { ...state, result: action.result };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const JobContext = createContext<{ state: JobState; dispatch: Dispatch<JobAction> } | null>(null);

export function JobProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return <JobContext.Provider value={{ state, dispatch }}>{children}</JobContext.Provider>;
}

export function useJobContext() {
  const ctx = useContext(JobContext);
  if (!ctx) throw new Error("useJobContext must be used within a JobProvider");
  return ctx;
}
