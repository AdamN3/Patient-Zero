"use client";

import { useEffect, useMemo, useState } from "react";

import type { EquityResponse, FeedbackResponse, Variant } from "@/lib/api";
import { parseFeedback, safetyLooksMissed } from "@/lib/feedback";
import MarkdownLite from "@/components/MarkdownLite";
import ScoreRing, { scoreTone } from "@/components/ScoreRing";

interface FeedbackProps {
  variant: Variant;
  feedback: FeedbackResponse | null;
  loading: boolean;
  /** Set when the feedback request itself failed (banner shows the detail). */
  failed: boolean;
  onRetryFeedback: () => void;
  onTryAgain: () => void;
  scores: Record<string, number>;
  variants: Variant[] | null;
  equity: EquityResponse | null;
}

/** Screen 3 — the assessor's report. */
export default function Feedback({
  variant,
  feedback,
  loading,
  failed,
  onRetryFeedback,
  onTryAgain,
  scores,
  variants,
  equity,
}: FeedbackProps) {
  const sections = useMemo(
    () => (feedback ? parseFeedback(feedback.feedback_markdown) : null),
    [feedback],
  );

  const safetyRow = feedback?.breakdown.find((row) =>
    /clinical reasoning and safety/i.test(row.category),
  );
  const safetyMissed =
    !!sections &&
    (safetyLooksMissed(sections.safety) ||
      (safetyRow?.score !== null && safetyRow !== undefined && safetyRow.score < safetyRow.max / 2));

  if (loading) return <LoadingState variantLabel={variant.label} />;

  if (!feedback) {
    return (
      <main className="mx-auto flex min-h-dvh w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
        <p className="text-lg text-slate-200">
          {failed ? "The assessor could not grade this interview." : "No feedback available."}
        </p>
        <p className="mt-2 text-sm text-slate-500">
          Your transcript is still here — you can retry without re-interviewing.
        </p>
        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onRetryFeedback}
            className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-500"
          >
            Retry feedback
          </button>
          <button
            type="button"
            onClick={onTryAgain}
            className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
          >
            Start over
          </button>
        </div>
      </main>
    );
  }

  const tone = scoreTone(feedback.overall_score);
  const labelFor = (id: string) => variants?.find((v) => v.id === id)?.label ?? id;

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
      {feedback.truncated && (
        <div
          role="status"
          className="mb-6 rounded-lg border border-amber-500/40 bg-amber-950/40 px-4 py-2.5 text-sm text-amber-200"
        >
          Feedback may be incomplete — the assessor hit its output limit.
        </div>
      )}

      {/* Score header */}
      <section className="flex flex-col items-center gap-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-8 md:flex-row md:items-center md:justify-between">
        <div className="text-center md:text-left">
          <p className="text-xs font-medium uppercase tracking-[0.3em] text-slate-500">
            Interview feedback · {variant.label}
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-50 sm:text-5xl">
            OVERALL SCORE:{" "}
            <span className={tone.text}>
              {feedback.overall_score ?? "—"}
              <span className="text-slate-500">/100</span>
            </span>
          </h1>
          <p className={`mt-2 text-sm font-medium ${tone.text}`}>{tone.label}</p>
          {sections?.preamble && (
            <div className="mt-4 max-w-xl">
              <MarkdownLite text={sections.preamble} />
            </div>
          )}
        </div>
        <ScoreRing score={feedback.overall_score} />
      </section>

      {/* Breakdown */}
      <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
        <h2 className="text-sm font-medium uppercase tracking-wider text-slate-400">
          Score breakdown
        </h2>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider text-slate-500">
              <th className="pb-2 font-medium">Category</th>
              <th className="pb-2 font-medium">Score</th>
              <th className="pb-2 text-right font-medium">Max</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {feedback.breakdown.map((row) => {
              const rowTone = scoreTone(row.score, row.max);
              const pct = row.score === null ? 0 : Math.round((row.score / row.max) * 100);
              return (
                <tr key={row.category}>
                  <td className="py-3 pr-4 text-slate-200">{row.category}</td>
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-3">
                      <span className={`w-8 font-mono tabular-nums ${rowTone.text}`}>
                        {row.score ?? "—"}
                      </span>
                      <div className="h-1.5 w-full max-w-[220px] overflow-hidden rounded-full bg-slate-800">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${pct}%`, backgroundColor: rowTone.stroke }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-right font-mono tabular-nums text-slate-500">
                    {row.max}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {sections?.breakdown && (
          <details className="mt-4 text-sm">
            <summary className="cursor-pointer text-slate-500 hover:text-slate-300">
              Assessor&apos;s notes per category
            </summary>
            <div className="mt-3 border-l border-slate-800 pl-4">
              <MarkdownLite text={sections.breakdown} />
            </div>
          </details>
        )}
      </section>

      {/* Narrative sections */}
      <section className="mt-6 grid gap-6 md:grid-cols-2">
        <Panel title="What You Did Well" accent="teal">
          <MarkdownLite text={sections?.didWell ?? ""} emptyText="No specific strengths were listed." />
        </Panel>
        <Panel title="What You Missed" accent="amber">
          <MarkdownLite text={sections?.missed ?? ""} emptyText="Nothing was flagged as missed." />
        </Panel>
        <Panel title="Top 3 Next Steps" accent="slate">
          <MarkdownLite text={sections?.nextSteps ?? ""} emptyText="No next steps were provided." />
        </Panel>
        <Panel
          title="Safety Assessment"
          accent={safetyMissed ? "red" : "green"}
          badge={safetyMissed ? "Emergency not recognised" : "Emergency recognised"}
        >
          <MarkdownLite
            text={sections?.safety ?? ""}
            emptyText="The assessor did not include a safety assessment."
          />
        </Panel>
      </section>

      {/* Equity check — only once two or more variants have been scored */}
      {Object.keys(scores).length >= 2 && (
        <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
          <h2 className="text-sm font-medium uppercase tracking-wider text-slate-400">
            Equity check
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Same case, same medicine — only the patient&apos;s demographics changed.
          </p>
          <ul className="mt-4 space-y-2">
            {Object.entries(scores).map(([id, score]) => {
              const rowTone = scoreTone(score);
              return (
                <li key={id} className="flex items-center gap-3 text-sm">
                  <span className="w-64 truncate text-slate-300">{labelFor(id)}</span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${score}%`, backgroundColor: rowTone.stroke }}
                    />
                  </div>
                  <span className={`w-10 text-right font-mono tabular-nums ${rowTone.text}`}>
                    {score}
                  </span>
                </li>
              );
            })}
          </ul>
          {equity && (
            <p
              className={`mt-4 rounded-md px-3 py-2 text-sm ${
                equity.gap === 0
                  ? "border border-teal-500/30 bg-teal-950/30 text-teal-200"
                  : "border border-amber-500/30 bg-amber-950/30 text-amber-200"
              }`}
            >
              {equity.message}
            </p>
          )}
        </section>
      )}

      {/* Raw report + actions */}
      <details className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/40 p-5 text-sm">
        <summary className="cursor-pointer text-slate-500 hover:text-slate-300">
          Full report (raw)
        </summary>
        <pre className="mt-4 whitespace-pre-wrap font-mono text-xs leading-relaxed text-slate-400">
          {feedback.feedback_markdown}
        </pre>
      </details>

      <div className="mt-10 flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={onTryAgain}
          className="rounded-md bg-teal-600 px-6 py-3 text-sm font-medium text-white hover:bg-teal-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
        >
          Try Again
        </button>
        <p className="text-xs text-slate-600">
          Educational simulation only. Not intended for real-world diagnosis or patient care.
        </p>
      </div>
    </main>
  );
}

// ---------------------------------------------------------------------------

function LoadingState({ variantLabel }: { variantLabel: string }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const started = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 500);
    return () => clearInterval(timer);
  }, []);

  return (
    <main
      className="mx-auto flex min-h-dvh w-full max-w-3xl flex-col items-center justify-center px-6 text-center"
      aria-busy
    >
      <div className="relative h-16 w-16">
        <span className="absolute inset-0 rounded-full border-2 border-slate-800" />
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-teal-400" />
      </div>
      <h1 className="mt-8 text-2xl font-medium text-slate-100">Assessing your interview</h1>
      <p className="mt-2 text-sm text-slate-400">
        Grading {variantLabel} against the history checklist, Calgary–Cambridge codebook and NICE
        CG95.
      </p>
      <p className="mt-6 font-mono text-xs text-slate-600">
        This usually takes 10–15 seconds · {elapsed}s
      </p>
    </main>
  );
}

type Accent = "teal" | "amber" | "slate" | "red" | "green";

const ACCENTS: Record<Accent, { border: string; title: string; badge: string }> = {
  teal: { border: "border-slate-800", title: "text-teal-300", badge: "" },
  amber: { border: "border-slate-800", title: "text-amber-300", badge: "" },
  slate: { border: "border-slate-800", title: "text-slate-200", badge: "" },
  red: {
    border: "border-red-500/60 bg-red-950/30 shadow-[inset_0_0_0_1px_rgba(239,68,68,0.15)]",
    title: "text-red-300",
    badge: "border-red-500/50 bg-red-500/15 text-red-200",
  },
  green: {
    border: "border-emerald-500/40 bg-emerald-950/20",
    title: "text-emerald-300",
    badge: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  },
};

function Panel({
  title,
  accent,
  badge,
  children,
}: {
  title: string;
  accent: Accent;
  badge?: string;
  children: React.ReactNode;
}) {
  const styles = ACCENTS[accent];
  return (
    <section className={`rounded-2xl border bg-slate-900/70 p-6 ${styles.border}`}>
      <div className="flex items-center justify-between gap-3">
        <h2 className={`text-sm font-medium uppercase tracking-wider ${styles.title}`}>{title}</h2>
        {badge && (
          <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${styles.badge}`}>
            {badge}
          </span>
        )}
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}
