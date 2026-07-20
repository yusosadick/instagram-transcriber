import { useClipboard } from "../hooks/useClipboard";

export function CopyButton({ text }: { text: string }) {
  const { copy, copied } = useClipboard();

  return (
    <button
      type="button"
      onClick={() => copy(text)}
      className="rounded-xl border border-stone-200 px-4 py-2 text-sm font-medium text-stone-600 shadow-soft transition hover:bg-stone-50 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
    >
      {copied ? "Copied!" : "Copy transcript"}
    </button>
  );
}
