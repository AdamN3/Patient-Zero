"use client";

interface ErrorBannerProps {
  message: string | null;
  onDismiss: () => void;
}

/** Fixed-position banner shown whenever an API call fails. Never silent. */
export default function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  if (!message) return null;

  return (
    <div
      role="alert"
      className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4 pointer-events-none"
    >
      <div className="pointer-events-auto flex w-full max-w-3xl items-start gap-3 rounded-lg border border-red-500/40 bg-red-950/90 px-4 py-3 text-sm text-red-100 shadow-lg shadow-red-950/40 backdrop-blur">
        <span
          aria-hidden
          className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-500/20 text-red-300"
        >
          !
        </span>
        <p className="flex-1 leading-snug">{message}</p>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded px-2 py-0.5 text-xs font-medium text-red-200 hover:bg-red-500/20 hover:text-white"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
