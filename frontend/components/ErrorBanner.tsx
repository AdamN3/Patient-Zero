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
      <div className="pointer-events-auto flex w-full max-w-3xl items-start gap-3 rounded-lg border border-red-200 bg-white px-4 py-3 text-sm text-red-700 shadow-[0_13px_27px_-5px_rgba(50,50,93,0.25),0_8px_16px_-8px_rgba(0,0,0,0.3)]">
        <span
          aria-hidden
          className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 font-semibold text-red-600"
        >
          !
        </span>
        <p className="flex-1 leading-snug">{message}</p>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded px-2 py-0.5 text-xs font-medium text-red-500 hover:bg-red-50 hover:text-red-700"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
