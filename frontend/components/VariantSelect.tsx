"use client";

import type { Variant } from "@/lib/api";

interface VariantSelectProps {
  variants: Variant[] | null;
  loading: boolean;
  onRetry: () => void;
  onBegin: (variant: Variant) => void;
  /** Scores from interviews finished earlier in this browser session. */
  scores: Record<string, number>;
  onClearScores: () => void;
}

/** Screen 1 — pick which patient variant to interview. */
export default function VariantSelect({
  variants,
  loading,
  onRetry,
  onBegin,
  scores,
  onClearScores,
}: VariantSelectProps) {
  const scoredCount = Object.keys(scores).length;

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6 py-14">
      <header className="mb-12 text-center">
        <p className="mb-3 text-xs font-medium uppercase tracking-[0.3em] text-teal-400/80">
          Standardized patient training
        </p>
        <h1 className="text-5xl font-semibold tracking-tight text-slate-50">Patient Zero</h1>
        <p className="mt-3 text-lg text-slate-400">Medical Interview Simulation</p>
        <p className="mx-auto mt-6 max-w-2xl text-sm leading-relaxed text-slate-500">
          You are the clinician. Take a focused history from the patient, commit to a working
          diagnosis and immediate plan, then receive structured feedback graded against the case
          checklist, the Calgary–Cambridge communication codebook and NICE CG95.
        </p>
      </header>

      {loading && (
        <div className="grid gap-5 md:grid-cols-3" aria-busy>
          {[0, 1, 2].map((index) => (
            <div
              key={index}
              className="h-56 animate-pulse rounded-xl border border-slate-800 bg-slate-900/60"
            />
          ))}
        </div>
      )}

      {!loading && variants && variants.length > 0 && (
        <section className="grid gap-5 md:grid-cols-3" aria-label="Patient variants">
          {variants.map((variant, index) => {
            const previous = scores[variant.id];
            return (
              <article
                key={variant.id}
                className="group flex flex-col rounded-xl border border-slate-800 bg-slate-900/70 p-6 transition-colors hover:border-teal-500/40 hover:bg-slate-900"
              >
                <div className="mb-4 flex items-start justify-between">
                  <span className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-700 bg-slate-800 font-mono text-sm text-slate-300">
                    {String.fromCharCode(65 + index)}
                  </span>
                  {previous !== undefined && (
                    <span className="rounded-full border border-slate-700 px-2.5 py-0.5 font-mono text-xs text-slate-400">
                      last {previous}/100
                    </span>
                  )}
                </div>
                <h2 className="text-lg font-medium text-slate-100">{variant.label}</h2>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-400">
                  {variant.demographics}
                </p>
                <button
                  type="button"
                  onClick={() => onBegin(variant)}
                  className="mt-6 w-full rounded-md bg-teal-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-teal-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
                >
                  Begin Interview
                </button>
              </article>
            );
          })}
        </section>
      )}

      {!loading && variants && variants.length === 0 && (
        <p className="text-center text-slate-400">The backend returned no patient variants.</p>
      )}

      {!loading && variants === null && (
        <div className="mx-auto max-w-md rounded-xl border border-slate-800 bg-slate-900/70 p-6 text-center">
          <p className="text-sm text-slate-400">
            Could not load patient variants from the backend.
          </p>
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:border-slate-500 hover:bg-slate-800"
          >
            Retry
          </button>
        </div>
      )}

      <footer className="mt-14 flex flex-col items-center gap-3 text-center text-xs text-slate-600">
        <p>
          Same clinical case every time — only the patient&apos;s demographics change. Finish two or
          more variants to see the equity check.
        </p>
        {scoredCount > 0 && (
          <button
            type="button"
            onClick={onClearScores}
            className="text-slate-500 underline-offset-4 hover:text-slate-300 hover:underline"
          >
            Clear {scoredCount} saved score{scoredCount === 1 ? "" : "s"}
          </button>
        )}
        <p>Educational simulation only. Not intended for real-world diagnosis or patient care.</p>
      </footer>
    </main>
  );
}
