"use client";

interface PatientAvatarProps {
  /** True while the patient is "speaking" (audio playing or reply streaming in). */
  speaking?: boolean;
  size?: "sm" | "lg";
}

/**
 * Placeholder for the patient's face.
 *
 * // TODO: ElevenLabs avatar goes here
 * Replace the inner <div> with the ElevenLabs conversational-avatar embed /
 * <video> element. Keep the outer wrapper so the chat layout is unchanged.
 * The `speaking` prop is already wired so the avatar can animate on playback.
 */
export default function PatientAvatar({ speaking = false, size = "sm" }: PatientAvatarProps) {
  const dimension = size === "lg" ? "h-16 w-16" : "h-9 w-9";
  const ring = speaking ? "ring-2 ring-teal-400/70 shadow-[0_0_18px_rgba(45,212,191,0.35)]" : "ring-1 ring-slate-700";

  return (
    <div
      aria-label="Patient avatar"
      data-elevenlabs-avatar-slot
      className={`${dimension} ${ring} relative shrink-0 select-none overflow-hidden rounded-full bg-slate-800 transition-shadow`}
    >
      {/* Generic silhouette until the ElevenLabs avatar is dropped in. */}
      <svg viewBox="0 0 40 40" className="h-full w-full text-slate-500" aria-hidden>
        <circle cx="20" cy="15" r="7" fill="currentColor" />
        <path d="M6 36c1.5-8 7.5-12 14-12s12.5 4 14 12H6z" fill="currentColor" />
      </svg>
      {speaking && (
        <span className="absolute inset-0 rounded-full border border-teal-300/40 animate-ping" />
      )}
    </div>
  );
}
