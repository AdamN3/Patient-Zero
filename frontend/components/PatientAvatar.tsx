"use client";

/* eslint-disable @next/next/no-img-element -- static local avatars, no next/image needed */

interface PatientAvatarProps {
  /** Variant id ("patient_a" | "patient_b" | "patient_c") → /public/{id}.jpg */
  variantId?: string;
  /** True while the patient is "speaking" (audio playing or reply streaming in). */
  speaking?: boolean;
  size?: "sm" | "lg" | "xl";
}

const SIZES = { sm: "h-10 w-10", lg: "h-16 w-16", xl: "h-24 w-24" } as const;

/**
 * The patient's face.
 *
 * // TODO: ElevenLabs avatar goes here
 * Replace the <img> with the ElevenLabs conversational-avatar embed / <video>
 * element. Keep the outer wrapper so the chat layout is unchanged. The
 * `speaking` prop is already wired so the avatar can animate on playback.
 */
export default function PatientAvatar({
  variantId,
  speaking = false,
  size = "sm",
}: PatientAvatarProps) {
  const ring = speaking
    ? "ring-2 ring-[#635bff] shadow-[0_0_18px_rgba(99,91,255,0.45)]"
    : "ring-1 ring-slate-200";

  return (
    <div
      aria-label="Patient avatar"
      data-elevenlabs-avatar-slot
      className={`${SIZES[size]} ${ring} relative shrink-0 select-none overflow-hidden rounded-full bg-slate-100 shadow-sm transition-shadow`}
    >
      {variantId ? (
        <img
          src={`/${variantId}.jpg`}
          alt="Patient portrait"
          className="h-full w-full object-cover"
          draggable={false}
        />
      ) : (
        <svg viewBox="0 0 40 40" className="h-full w-full text-slate-300" aria-hidden>
          <circle cx="20" cy="15" r="7" fill="currentColor" />
          <path d="M6 36c1.5-8 7.5-12 14-12s12.5 4 14 12H6z" fill="currentColor" />
        </svg>
      )}
      {speaking && (
        <span className="absolute inset-0 rounded-full border-2 border-[#635bff]/40 animate-ping" />
      )}
    </div>
  );
}
