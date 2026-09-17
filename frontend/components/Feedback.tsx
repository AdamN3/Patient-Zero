"use client";

import { useEffect, useMemo, useState } from "react";

import type { EquityResponse, FeedbackResponse, Variant } from "@/lib/api";
import { parseFeedback, safetyLooksMissed } from "@/lib/feedback";
import MarkdownLite from "@/components/MarkdownLite";
import PatientAvatar from "@/components/PatientAvatar";
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
        <p className="text-lg font-medium text-[#0a2540]">
          {failed ? "The assessor could not grade this interview." : "No feedback available."}
        </p>
        <p className="mt-2 text-sm text-[#425466]">
          Your transcript is still here — you can retry without re-interviewing.
        </p>
        <div className="mt-6 flex gap-3">
          <button type="button" onClick={onRetryFeedback} className="pz-btn px-4 py-2 text-sm">
            Retry feedback
          </button>
          <button
            type="button"
            onClick={onTryAgain}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-[#0a2540] shadow-sm hover:border-[#635bff]/40 hover:text-[#635bff]"
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
          className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-700"
        >
          Feedback may be incomplete — the assessor hit its output limit.
        </div>
      )}

      {/* Score header */}
      <section className="pz-card flex flex-col items-center gap-8 p-8 md:flex-row md:items-center md:justify-between">
        <div className="text-center md:text-left">
          <div className="flex items-center justify-center gap-3 md:justify-start">
            <PatientAvatar variantId={variant.id} />
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
              Interview feedback · {variant.label}
            </p>
          </div>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-[#0a2540] sm:text-5xl">
            OVERALL SCORE:{" "}
            <span className={tone.text}>
              {feedback.overall_score ?? "—"}
              <span className="text-slate-300">/100</span>
            </span>
          </h1>
          <p className={`mt-2 text-sm font-semibold ${tone.text}`}>{tone.label}</p>
          {sections?.preamble && (
            <div className="mt-4 max-w-xl">
              <MarkdownLite text={sections.preamble} />
            </div>
          )}
        </div>
        <ScoreRing score={feedback.overall_score} />
      </section>

      {/* Breakdown */}
      <section className="pz-card mt-6 p-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-[#0a2540]">
          Score breakdown
        </h2>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider text-slate-400">
              <th className="pb-2 font-semibold">Category</th>
              <th className="pb-2 font-semibold">Score</th>
              <th className="pb-2 text-right font-semibold">Max</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {feedback.breakdown.map((row) => {
              const rowTone = scoreTone(row.score, row.max);
              const pct = row.score === null ? 0 : Math.round((row.score / row.max) * 100);
              return (
                <tr key={row.category}>
                  <td className="py-3 pr-4 font-medium text-[#0a2540]">{row.category}</td>
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-3">
                      <span className={`w-8 font-mono font-semibold tabular-nums ${rowTone.text}`}>
                        {row.score ?? "—"}
                      </span>
                      <div className="h-2 w-full max-w-[220px] overflow-hidden rounded-full bg-slate-100">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${pct}%`, backgroundColor: rowTone.stroke }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-right font-mono tabular-nums text-slate-400">
                    {row.max}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {sections?.breakdown && (
          <details className="mt-4 text-sm">
            <summary className="cursor-pointer font-medium text-[#635bff] hover:text-[#0a2540]">
              Assessor&apos;s notes per category
            </summary>
            <div className="mt-3 border-l-2 border-[#635bff]/20 pl-4">
              <MarkdownLite text={sections.breakdown} />
            </div>
          </details>
        )}
      </section>

      {/* Narrative sections */}
      <section className="mt-6 grid gap-6 md:grid-cols-2">
        <Panel title="What You Did Well" accent="green">
          <MarkdownLite text={sections?.didWell ?? ""} emptyText="No specific strengths were listed." />
        </Panel>
        <Panel title="What You Missed" accent="amber">
          <MarkdownLite text={sections?.missed ?? ""} emptyText="Nothing was flagged as missed." />
        </Panel>
        <Panel title="Top 3 Next Steps" accent="indigo">
          <MarkdownLite text={sections?.nextSteps ?? ""} emptyText="No next steps were provided." />
        </Panel>
        <Panel
          title="Safety Assessment"
          accent={safetyMissed ? "red" : "success"}
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
        <section className="pz-card mt-6 p-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-[#0a2540]">
            Equity check
          </h2>
          <p className="mt-1 text-xs text-slate-400">
            Same case, same medicine — only the patient&apos;s demographics changed.
          </p>
          <ul className="mt-4 space-y-2">
            {Object.entries(scores).map(([id, score]) => {
              const rowTone = scoreTone(score);
              return (
                <li key={id} className="flex items-center gap-3 text-sm">
                  <span className="w-64 truncate font-medium text-[#0a2540]">{labelFor(id)}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${score}%`, backgroundColor: rowTone.stroke }}
                    />
                  </div>
                  <span className={`w-10 text-right font-mono font-semibold tabular-nums ${rowTone.text}`}>
                    {score}
                  </span>
                </li>
              );
            })}
          </ul>
          {equity && (
            <p
              className={`mt-4 rounded-lg px-3 py-2 text-sm font-medium ${
                equity.gap === 0
                  ? "border border-[#00c853]/30 bg-[#00c853]/10 text-[#00893a]"
                  : "border border-amber-200 bg-amber-50 text-amber-700"
              }`}
            >
              {equity.message}
            </p>
          )}
        </section>
      )}

      {/* Raw report + actions */}
      <details className="pz-card mt-6 p-5 text-sm">
        <summary className="cursor-pointer font-medium text-[#635bff] hover:text-[#0a2540]">
          Full report (raw)
        </summary>
        <pre className="mt-4 whitespace-pre-wrap font-mono text-xs leading-relaxed text-[#425466]">
          {feedback.feedback_markdown}
        </pre>
      </details>

      <div className="mt-10 flex flex-col items-center gap-3">
        <button type="button" onClick={onTryAgain} className="pz-btn px-8 py-3 text-sm">
          Try Again
        </button>
        <p className="text-xs text-slate-400">
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
        <span className="absolute inset-0 rounded-full border-2 border-slate-200" />
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-[#635bff]" />
      </div>
      <h1 className="mt-8 text-2xl font-semibold text-[#0a2540]">Assessing your interview</h1>
      <p className="mt-2 text-sm text-[#425466]">
        Grading {variantLabel} against the history checklist, Calgary–Cambridge codebook and NICE
        CG95.
      </p>
      <p className="mt-6 font-mono text-xs text-slate-400">
        This usually takes 10–15 seconds · {elapsed}s
      </p>
    </main>
  );
}

type Accent = "green" | "amber" | "indigo" | "red" | "success";

const ACCENTS: Record<Accent, { card: string; title: string; badge: string }> = {
  green: { card: "", title: "text-[#00893a]", badge: "" },
  amber: { card: "", title: "text-[#d48806]", badge: "" },
  indigo: { card: "", title: "text-[#635bff]", badge: "" },
  red: {
    card: "border border-red-300 bg-red-50/60",
    title: "text-red-600",
    badge: "border-red-300 bg-red-100 text-red-700",
  },
  success: {
    card: "border border-[#00c853]/40 bg-[#00c853]/5",
    title: "text-[#00893a]",
    badge: "border-[#00c853]/40 bg-[#00c853]/10 text-[#00893a]",
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
    <section className={`pz-card p-6 ${styles.card}`}>
      <div className="flex items-center justify-between gap-3">
        <h2 className={`text-sm font-semibold uppercase tracking-wider ${styles.title}`}>{title}</h2>
        {badge && (
          <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${styles.badge}`}>
            {badge}
          </span>
        )}
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}
