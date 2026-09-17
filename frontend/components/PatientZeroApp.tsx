"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  describeError,
  getVariants,
  postChat,
  postEquity,
  postFeedback,
  userMessage,
  type BedrockMessage,
  type EquityResponse,
  type FeedbackResponse,
  type Variant,
} from "@/lib/api";
import ErrorBanner from "@/components/ErrorBanner";
import Feedback from "@/components/Feedback";
import Interview from "@/components/Interview";
import VariantSelect from "@/components/VariantSelect";

type Phase = "select" | "interview" | "feedback";

/**
 * Single source of truth for the whole simulation. All API state — the Bedrock
 * `messages` array, the chosen variant, per-variant scores — lives here and is
 * passed down as props. Nothing is persisted; a refresh starts over.
 */
export default function PatientZeroApp() {
  const [phase, setPhase] = useState<Phase>("select");
  const [error, setError] = useState<string | null>(null);

  // Screen 1
  const [variants, setVariants] = useState<Variant[] | null>(null);
  const [variantsLoading, setVariantsLoading] = useState(true);

  // Screen 2
  const [variant, setVariant] = useState<Variant | null>(null);
  const [messages, setMessages] = useState<BedrockMessage[]>([]);
  const [guardrailIndices, setGuardrailIndices] = useState<number[]>([]);
  const [sending, setSending] = useState(false);
  const [clinicalImpression, setClinicalImpression] = useState("");
  const [speaking, setSpeaking] = useState(false);

  // Screen 3
  const [feedback, setFeedback] = useState<FeedbackResponse | null>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackFailed, setFeedbackFailed] = useState(false);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [equity, setEquity] = useState<EquityResponse | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // ------------------------------------------------------------------ variants

  // State is only touched inside promise callbacks, so this is safe to call
  // from an effect (no synchronous setState).
  const loadVariants = useCallback(() => {
    return getVariants()
      .then((list) => setVariants(list))
      .catch((err: unknown) => {
        setVariants(null);
        setError(describeError(err));
      })
      .finally(() => setVariantsLoading(false));
  }, []);

  const retryVariants = useCallback(() => {
    setVariantsLoading(true);
    void loadVariants();
  }, [loadVariants]);

  useEffect(() => {
    void loadVariants();
  }, [loadVariants]);

  // --------------------------------------------------------------------- audio

  const stopAudio = useCallback(() => {
    audioRef.current?.pause();
    audioRef.current = null;
    setSpeaking(false);
  }, []);

  /**
   * Plays the Polly MP3 the backend returns when `voice: true`.
   * // TODO: ElevenLabs voice can replace this — swap the data-URL <audio> for
   * // the ElevenLabs TTS/stream and keep the setSpeaking() calls so the avatar animates.
   */
  const playPatientAudio = useCallback(
    (audioBase64: string) => {
      stopAudio();
      const audio = new Audio(`data:audio/mpeg;base64,${audioBase64}`);
      audioRef.current = audio;
      audio.onplay = () => setSpeaking(true);
      audio.onended = () => setSpeaking(false);
      audio.onpause = () => setSpeaking(false);
      audio.onerror = () => setSpeaking(false);
      // Autoplay is allowed here because the user just clicked Send; if the
      // browser still refuses, degrade silently to text (the message is shown).
      audio.play().catch(() => setSpeaking(false));
    },
    [stopAudio],
  );

  useEffect(() => stopAudio, [stopAudio]);

  // ------------------------------------------------------------------ actions

  function beginInterview(chosen: Variant) {
    stopAudio();
    setVariant(chosen);
    setMessages([]);
    setGuardrailIndices([]);
    setClinicalImpression("");
    setFeedback(null);
    setFeedbackFailed(false);
    setEquity(null);
    setError(null);
    setPhase("interview");
  }

  /** Send one student question. Returns false (after rolling back) on failure. */
  async function sendQuestion(text: string): Promise<boolean> {
    if (!variant || sending) return false;

    const outgoing = [...messages, userMessage(text)];
    setMessages(outgoing); // optimistic
    setSending(true);
    setError(null);

    try {
      const reply = await postChat({
        variant: variant.id,
        messages: outgoing,
        voice: false,
      });

      const patientMessage: BedrockMessage =
        reply.message?.role === "assistant" && Array.isArray(reply.message.content)
          ? reply.message
          : { role: "assistant", content: [{ text: reply.text }] };

      setMessages([...outgoing, patientMessage]);
      if (reply.guardrail) {
        setGuardrailIndices((prev) => [...prev, outgoing.length]);
      }
      if (reply.audio_base64) playPatientAudio(reply.audio_base64);
      return true;
    } catch (err) {
      setMessages(messages); // roll back the optimistic user turn
      setError(describeError(err));
      return false;
    } finally {
      setSending(false);
    }
  }

  async function requestFeedback(
    transcript: BedrockMessage[],
    impression: string,
    forVariant: Variant,
  ) {
    setFeedbackLoading(true);
    setFeedbackFailed(false);
    setError(null);

    try {
      const result = await postFeedback({
        messages: transcript,
        clinical_impression: impression.trim(),
      });
      setFeedback(result);

      if (result.overall_score !== null) {
        const nextScores = { ...scores, [forVariant.id]: result.overall_score };
        setScores(nextScores);

        if (Object.keys(nextScores).length >= 2) {
          try {
            setEquity(await postEquity(nextScores));
          } catch (equityErr) {
            setEquity(null);
            setError(`Equity check unavailable — ${describeError(equityErr)}`);
          }
        }
      }
    } catch (err) {
      setFeedback(null);
      setFeedbackFailed(true);
      setError(describeError(err));
    } finally {
      setFeedbackLoading(false);
    }
  }

  function endInterview() {
    if (!variant || messages.length === 0 || !clinicalImpression.trim()) return;
    stopAudio();
    setPhase("feedback");
    void requestFeedback(messages, clinicalImpression, variant);
  }

  function retryFeedback() {
    if (!variant) return;
    void requestFeedback(messages, clinicalImpression, variant);
  }

  /** Back to Screen 1. Per-variant scores are kept so the equity check can compare runs. */
  function tryAgain() {
    stopAudio();
    setVariant(null);
    setMessages([]);
    setGuardrailIndices([]);
    setClinicalImpression("");
    setFeedback(null);
    setFeedbackFailed(false);
    setEquity(null);
    setError(null);
    setPhase("select");
    if (variants === null) retryVariants();
  }

  // ------------------------------------------------------------------- render

  return (
    <>
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {phase === "select" && (
        <VariantSelect
          variants={variants}
          loading={variantsLoading}
          onRetry={retryVariants}
          onBegin={beginInterview}
          scores={scores}
          onClearScores={() => {
            setScores({});
            setEquity(null);
          }}
        />
      )}

      {phase === "interview" && variant && (
        <Interview
          variant={variant}
          messages={messages}
          guardrailIndices={guardrailIndices}
          sending={sending}
          speaking={speaking}
          clinicalImpression={clinicalImpression}
          onImpressionChange={setClinicalImpression}
          onSend={sendQuestion}
          onEnd={endInterview}
          onAbandon={tryAgain}
        />
      )}

      {phase === "feedback" && variant && (
        <Feedback
          variant={variant}
          feedback={feedback}
          loading={feedbackLoading}
          failed={feedbackFailed}
          onRetryFeedback={retryFeedback}
          onTryAgain={tryAgain}
          scores={scores}
          variants={variants}
          equity={equity}
        />
      )}
    </>
  );
}
