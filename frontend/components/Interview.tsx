"use client";

import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";

import { messageText, type BedrockMessage, type Variant } from "@/lib/api";
import PatientAvatar from "@/components/PatientAvatar";

interface InterviewProps {
  variant: Variant;
  messages: BedrockMessage[];
  /** Indices into `messages` whose patient reply was a guardrail decline. */
  guardrailIndices: number[];
  sending: boolean;
  /** True while patient audio is playing (drives the avatar animation). */
  speaking: boolean;
  clinicalImpression: string;
  onImpressionChange: (value: string) => void;
  /** Resolves true if the turn succeeded, false if it failed and was rolled back. */
  onSend: (text: string) => Promise<boolean>;
  onEnd: () => void;
  onAbandon: () => void;
}

const MAX_QUESTION_CHARS = 2000; // mirrors backend/app.py

/** Screen 2 — the live interview. */
export default function Interview({
  variant,
  messages,
  guardrailIndices,
  sending,
  speaking,
  clinicalImpression,
  onImpressionChange,
  onSend,
  onEnd,
  onAbandon,
}: InterviewProps) {
  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const questionCount = messages.filter((m) => m.role === "user").length;
  const hasExchange = messages.length > 0;
  const impressionReady = clinicalImpression.trim().length > 0;
  const canEnd = hasExchange && impressionReady && !sending;
  const canSend = draft.trim().length > 0 && !sending;

  // Keep the newest message in view.
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages.length, sending]);

  // Return focus to the input after each patient reply.
  useEffect(() => {
    if (!sending) inputRef.current?.focus();
  }, [sending]);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const text = draft.trim();
    if (!text || sending) return;

    setDraft("");
    const ok = await onSend(text);
    if (!ok) setDraft(text); // give the question back so it can be retried
  }

  function onImpressionKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Ctrl/Cmd+Enter in the impression box ends the interview if allowed.
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && canEnd) {
      event.preventDefault();
      onEnd();
    }
  }

  let endHint = "";
  if (!hasExchange) endHint = "Ask the patient at least one question first.";
  else if (!impressionReady) endHint = "Enter your clinical impression to finish.";
  else if (sending) endHint = "Waiting for the patient to respond…";

  return (
    <main className="mx-auto flex h-dvh w-full max-w-5xl flex-col px-4 py-4 sm:px-6">
      {/* Top bar */}
      <header className="pz-card flex items-center justify-between gap-4 px-5 py-3">
        <div className="flex min-w-0 items-center gap-4">
          <PatientAvatar variantId={variant.id} speaking={speaking} />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-[#0a2540]">{variant.label}</p>
            <p className="truncate text-xs text-[#425466]">{variant.demographics}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="hidden rounded-full bg-[#f6f9fc] px-3 py-1 font-mono text-xs font-medium text-[#635bff] sm:inline">
            {questionCount} question{questionCount === 1 ? "" : "s"}
          </span>
          <button
            type="button"
            onClick={onAbandon}
            className="rounded-md px-3 py-2 text-xs font-medium text-slate-400 hover:bg-slate-50 hover:text-[#0a2540]"
          >
            Abandon
          </button>
          <button
            type="button"
            onClick={onEnd}
            disabled={!canEnd}
            title={endHint || "Finish and get feedback"}
            className="pz-btn px-4 py-2 text-sm"
          >
            End Interview
          </button>
        </div>
      </header>

      {/* Chat window */}
      <section
        ref={scrollRef}
        aria-live="polite"
        aria-label="Conversation"
        className="pz-card my-4 flex-1 overflow-y-auto p-4 sm:p-6"
      >
        {messages.length === 0 && !sending && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <PatientAvatar variantId={variant.id} size="xl" />
            <p className="mt-5 text-sm font-medium text-[#0a2540]">The patient is waiting.</p>
            <p className="mt-1 max-w-sm text-xs leading-relaxed text-[#425466]">
              Introduce yourself and ask what brought them in today. They will only share what
              you specifically ask about.
            </p>
          </div>
        )}

        <ol className="space-y-4">
          {messages.map((message, index) => {
            const isStudent = message.role === "user";
            const isGuardrail = guardrailIndices.includes(index);
            const text = messageText(message);

            if (isStudent) {
              return (
                <li key={index} className="flex justify-end">
                  <div className="max-w-[78%]">
                    <p className="mb-1 text-right text-[11px] font-semibold uppercase tracking-wider text-[#635bff]">
                      You
                    </p>
                    <div className="rounded-2xl rounded-tr-sm border border-slate-200 bg-white px-4 py-2.5 text-sm leading-relaxed text-[#0a2540] shadow-sm">
                      {text}
                    </div>
                  </div>
                </li>
              );
            }

            return (
              <li key={index} className="flex items-end gap-3">
                {/* Avatar column — the ElevenLabs face will render inside PatientAvatar. */}
                <PatientAvatar
                  variantId={variant.id}
                  speaking={speaking && index === messages.length - 1}
                />
                <div className="max-w-[78%]">
                  <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Patient
                  </p>
                  <div
                    className={
                      isGuardrail
                        ? "rounded-2xl rounded-tl-sm border border-dashed border-slate-300 bg-slate-50 px-4 py-2.5 text-sm italic leading-relaxed text-slate-500"
                        : "rounded-2xl rounded-tl-sm bg-[#eeedff] px-4 py-2.5 text-sm leading-relaxed text-[#0a2540]"
                    }
                  >
                    {text}
                  </div>
                </div>
              </li>
            );
          })}

          {sending && (
            <li className="flex items-end gap-3" aria-label="Patient is responding">
              <PatientAvatar variantId={variant.id} speaking />
              <div>
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Patient
                </p>
                <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-[#eeedff] px-4 py-3">
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-[#635bff]" />
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-[#635bff]" />
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-[#635bff]" />
                </div>
              </div>
            </li>
          )}
        </ol>
      </section>

      {/* Composer */}
      <form onSubmit={submit} className="pz-card p-4">
        <label htmlFor="impression" className="flex items-baseline justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#0a2540]">
            Clinical impression
          </span>
          <span className="text-[11px] text-slate-400">
            Working diagnosis and immediate plan — required before ending
          </span>
        </label>
        <textarea
          id="impression"
          value={clinicalImpression}
          onChange={(event) => onImpressionChange(event.target.value)}
          onKeyDown={onImpressionKeyDown}
          rows={2}
          maxLength={4000}
          placeholder="e.g. Likely acute coronary syndrome. Immediate 12-lead ECG, troponin, senior review; do not discharge."
          className="mt-2 w-full resize-y rounded-lg border border-slate-200 bg-[#f6f9fc] px-3 py-2 text-sm text-[#0a2540] placeholder:text-slate-400 focus:border-[#635bff] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#635bff]/25"
        />

        <div className="mt-3 flex items-center gap-3">
          <input
            ref={inputRef}
            type="text"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            maxLength={MAX_QUESTION_CHARS}
            disabled={sending}
            placeholder="Ask the patient a question…"
            aria-label="Your question to the patient"
            autoComplete="off"
            className="flex-1 rounded-lg border border-slate-200 bg-[#f6f9fc] px-3 py-2.5 text-sm text-[#0a2540] placeholder:text-slate-400 focus:border-[#635bff] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#635bff]/25 disabled:opacity-60"
          />
          <button type="submit" disabled={!canSend} className="pz-btn px-5 py-2.5 text-sm">
            {sending ? "Sending…" : "Send"}
          </button>
        </div>

        {endHint && <p className="mt-2 text-[11px] text-slate-400">{endHint}</p>}
      </form>
    </main>
  );
}
