import { useState } from "react";

import { FileDropZone } from "./components/FileDropZone";
import { HistoryList } from "./components/HistoryList";
import { ProgressIndicator } from "./components/ProgressIndicator";
import { TranscriptView } from "./components/TranscriptView";
import { UrlInputForm } from "./components/UrlInputForm";
import { JobProvider, useJobContext } from "./context/JobContext";
import { useJobPolling } from "./hooks/useJobPolling";

type InputMode = "url" | "file";

function DarkModeToggle() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return (
    <button
      type="button"
      onClick={toggle}
      className="rounded-xl border border-stone-200 px-3 py-1.5 text-xs font-medium text-stone-600 transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
    >
      {dark ? "Light mode" : "Dark mode"}
    </button>
  );
}

function TranscriberPanel() {
  const { state } = useJobContext();
  const [mode, setMode] = useState<InputMode>("url");
  useJobPolling();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex gap-2">
        {(["url", "file"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
              mode === m
                ? "bg-brand-500 text-white shadow-soft"
                : "text-stone-500 hover:bg-stone-100 dark:text-stone-400 dark:hover:bg-stone-800"
            }`}
          >
            {m === "url" ? "Paste URL" : "Upload file"}
          </button>
        ))}
      </div>

      {mode === "url" ? <UrlInputForm /> : <FileDropZone />}

      <ProgressIndicator />

      {state.result && state.jobId && <TranscriptView jobId={state.jobId} result={state.result} />}

      <HistoryList />
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-surface-light dark:bg-surface-dark">
      <div className="mx-auto flex max-w-2xl flex-col gap-8 px-4 py-12">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-stone-800 dark:text-stone-100">
              Instagram Transcriber
            </h1>
            <p className="text-sm text-stone-500 dark:text-stone-400">
              Local, offline, zero-cost transcription for Reels and Posts.
            </p>
          </div>
          <DarkModeToggle />
        </header>

        <JobProvider>
          <TranscriberPanel />
        </JobProvider>
      </div>
    </div>
  );
}
