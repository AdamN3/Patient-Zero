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
      <header className="flex items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/70 px-5 py-3">
        <div className="flex min-w-0 items-center gap-4">
          <PatientAvatar speaking={speaking} />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-100">{variant.label}</p>
            <p className="truncate text-xs text-slate-400">{variant.demographics}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="hidden rounded-full border border-slate-800 px-3 py-1 font-mono text-xs text-slate-400 sm:inline">
            {questionCount} question{questionCount === 1 ? "" : "s"}
          </span>
          <button
            type="button"
            onClick={onAbandon}
            className="rounded-md px-3 py-2 text-xs text-slate-400 hover:bg-slate-800 hover:text-slate-200"
          >
            Abandon
          </button>
          <button
            type="button"
            onClick={onEnd}
            disabled={!canEnd}
            title={endHint || "Finish and get feedback"}
            className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-teal-500 disabled:cursor-not-allowed disabled:bg-slate-800 disabled:text-slate-500"
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
        className="my-4 flex-1 overflow-y-auto rounded-xl border border-slate-800 bg-slate-950/60 p-4 sm:p-6"
      >
        {messages.length === 0 && !sending && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <PatientAvatar size="lg" />
            <p className="mt-5 text-sm text-slate-300">The patient is waiting.</p>
            <p className="mt-1 max-w-sm text-xs leading-relaxed text-slate-500">
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
                    <p className="mb-1 text-right text-[11px] font-medium uppercase tracking-wider text-teal-400/80">
                      You
                    </p>
                    <div className="rounded-2xl rounded-tr-sm bg-teal-900/50 px-4 py-2.5 text-sm leading-relaxed text-teal-50 ring-1 ring-teal-700/40">
                      {text}
                    </div>
                  </div>
                </li>
              );
            }

            return (
              <li key={index} className="flex items-end gap-3">
                {/* Avatar column — the ElevenLabs face will render inside PatientAvatar. */}
                <PatientAvatar speaking={speaking && index === messages.length - 1} />
                <div className="max-w-[78%]">
                  <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-slate-500">
                    Patient
                  </p>
                  <div
                    className={
                      isGuardrail
                        ? "rounded-2xl rounded-tl-sm border border-dashed border-slate-600 bg-slate-900/40 px-4 py-2.5 text-sm italic leading-relaxed text-slate-400"
                        : "rounded-2xl rounded-tl-sm bg-slate-800 px-4 py-2.5 text-sm leading-relaxed text-slate-100 ring-1 ring-slate-700/60"
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
              <PatientAvatar speaking />
              <div>
                <p className="mb-1 text-[11px] font-medium uppercase tracking-wider text-slate-500">
                  Patient
                </p>
                <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-slate-800 px-4 py-3 ring-1 ring-slate-700/60">
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-slate-300" />
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-slate-300" />
                  <span className="pz-typing-dot h-1.5 w-1.5 rounded-full bg-slate-300" />
                </div>
              </div>
            </li>
          )}
        </ol>
      </section>

      {/* Composer */}
      <form
        onSubmit={submit}
        className="rounded-xl border border-slate-800 bg-slate-900/70 p-4"
      >
        <label htmlFor="impression" className="flex items-baseline justify-between">
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            Clinical impression
          </span>
          <span className="text-[11px] text-slate-600">
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
          className="mt-2 w-full resize-y rounded-md border border-slate-700 bg-slate-950/70 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500/60"
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
            className="flex-1 rounded-md border border-slate-700 bg-slate-950/70 px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-600 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500/60 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={!canSend}
            className="rounded-md bg-slate-100 px-5 py-2.5 text-sm font-medium text-slate-950 transition-colors hover:bg-white disabled:cursor-not-allowed disabled:bg-slate-800 disabled:text-slate-500"
          >
            {sending ? "Sending…" : "Send"}
          </button>
        </div>

        {endHint && (
          <p className="mt-2 text-[11px] text-slate-600">{endHint}</p>
        )}
      </form>
    </main>
  );
}
