"use client";

interface ScoreRingProps {
  score: number | null;
  max?: number;
  size?: number;
}

export function scoreTone(score: number | null, max = 100) {
  if (score === null) {
    return { stroke: "#8898aa", text: "text-slate-400", label: "Unscored" };
  }
  const pct = score / max;
  if (pct >= 0.75) return { stroke: "#00c853", text: "text-[#00a844]", label: "Strong" };
  if (pct >= 0.5) return { stroke: "#f5a623", text: "text-[#d48806]", label: "Developing" };
  return { stroke: "#ef4444", text: "text-[#dc2626]", label: "Needs work" };
}

/** SVG ring showing score / max. */
export default function ScoreRing({ score, max = 100, size = 168 }: ScoreRingProps) {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const fraction = score === null ? 0 : Math.max(0, Math.min(1, score / max));
  const dashOffset = circumference * (1 - fraction);
  const tone = scoreTone(score, max);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90" role="img" aria-label={`Score ${score ?? "unknown"} of ${max}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e3e8ee"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={tone.stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: "stroke-dashoffset 900ms ease-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold tabular-nums ${tone.text}`}>
          {score === null ? "—" : score}
        </span>
        <span className="text-xs font-medium uppercase tracking-widest text-slate-400">/ {max}</span>
      </div>
    </div>
  );
}
