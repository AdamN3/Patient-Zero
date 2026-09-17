"use client";

import type { Variant } from "@/lib/api";
import PatientAvatar from "@/components/PatientAvatar";

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
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-[#635bff]">
          Standardized patient training
        </p>
        <h1 className="bg-gradient-to-r from-[#0a2540] via-[#635bff] to-[#00d4ff] bg-clip-text text-5xl font-bold tracking-tight text-transparent">
          Patient Zero
        </h1>
        <p className="mt-3 text-lg font-medium text-[#0a2540]">Medical Interview Simulation</p>
        <p className="mx-auto mt-6 max-w-2xl text-sm leading-relaxed text-[#425466]">
          You are the clinician. Take a focused history from the patient, commit to a working
          diagnosis and immediate plan, then receive structured feedback graded against the case
          checklist, the Calgary–Cambridge communication codebook and NICE CG95.
        </p>
      </header>

      {loading && (
        <div className="grid gap-6 md:grid-cols-3" aria-busy>
          {[0, 1, 2].map((index) => (
            <div key={index} className="pz-card h-72 animate-pulse" />
          ))}
        </div>
      )}

      {!loading && variants && variants.length > 0 && (
        <section className="grid gap-6 md:grid-cols-3" aria-label="Patient variants">
          {variants.map((variant) => {
            const previous = scores[variant.id];
            return (
              <article
                key={variant.id}
                className="pz-card pz-card-hover flex flex-col items-center p-7 text-center"
              >
                <div className="relative">
                  <PatientAvatar variantId={variant.id} size="xl" />
                  {previous !== undefined && (
                    <span className="absolute -right-3 -top-1 rounded-full border border-slate-200 bg-white px-2 py-0.5 font-mono text-[11px] font-medium text-[#635bff] shadow-sm">
                      {previous}/100
                    </span>
                  )}
                </div>
                <h2 className="mt-5 text-lg font-semibold text-[#0a2540]">{variant.label}</h2>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-[#425466]">
                  {variant.demographics}
                </p>
                <button
                  type="button"
                  onClick={() => onBegin(variant)}
                  className="pz-btn mt-6 w-full px-4 py-2.5 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[#635bff] focus-visible:ring-offset-2"
                >
                  Begin Interview
                </button>
              </article>
            );
          })}
        </section>
      )}

      {!loading && variants && variants.length === 0 && (
        <p className="text-center text-[#425466]">The backend returned no patient variants.</p>
      )}

      {!loading && variants === null && (
        <div className="pz-card mx-auto max-w-md p-7 text-center">
          <p className="text-sm text-[#425466]">
            Could not load patient variants from the backend.
          </p>
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-[#0a2540] shadow-sm hover:border-[#635bff]/40 hover:text-[#635bff]"
          >
            Retry
          </button>
        </div>
      )}

      <footer className="mt-14 flex flex-col items-center gap-3 text-center text-xs text-slate-400">
        <p>
          Same clinical case every time — only the patient&apos;s demographics change. Finish two or
          more variants to see the equity check.
        </p>
        {scoredCount > 0 && (
          <button
            type="button"
            onClick={onClearScores}
            className="font-medium text-[#635bff] underline-offset-4 hover:underline"
          >
            Clear {scoredCount} saved score{scoredCount === 1 ? "" : "s"}
          </button>
        )}
        <p>Educational simulation only. Not intended for real-world diagnosis or patient care.</p>
      </footer>
    </main>
  );
}
