/**
 * Splits the assessor's markdown report into its named sections so the
 * feedback screen can lay them out individually.
 *
 * The model is asked for plain headings ("WHAT YOU DID WELL") but frequently
 * wraps them in markdown ("## What You Did Well", "**WHAT YOU MISSED**"), so
 * matching is done on a normalised form of each line.
 */

export type SectionKey =
  | "breakdown"
  | "didWell"
  | "missed"
  | "nextSteps"
  | "safety";

export interface FeedbackSections {
  /** Anything before the first recognised heading (minus the score line). */
  preamble: string;
  breakdown: string;
  didWell: string;
  missed: string;
  nextSteps: string;
  safety: string;
}

const HEADINGS: Array<{ key: SectionKey; match: RegExp }> = [
  { key: "breakdown", match: /^score breakdown$/ },
  { key: "didWell", match: /^what you did well$/ },
  { key: "missed", match: /^what you missed$/ },
  { key: "nextSteps", match: /^top ?3 next steps$/ },
  { key: "safety", match: /^safety assessment$/ },
];

/** Strip markdown heading/emphasis punctuation so "## **Foo:**" → "foo". */
function normaliseHeading(line: string): string {
  return line
    .replace(/^[\s#>*_\-]+/, "")
    .replace(/[\s*_:.\-—–]+$/, "")
    .trim()
    .toLowerCase();
}

function headingKey(line: string): SectionKey | null {
  const normalised = normaliseHeading(line);
  if (!normalised) return null;
  for (const heading of HEADINGS) {
    if (heading.match.test(normalised)) return heading.key;
  }
  return null;
}

export function parseFeedback(markdown: string): FeedbackSections {
  const sections: FeedbackSections = {
    preamble: "",
    breakdown: "",
    didWell: "",
    missed: "",
    nextSteps: "",
    safety: "",
  };

  let current: SectionKey | "preamble" = "preamble";
  const buffers: Record<SectionKey | "preamble", string[]> = {
    preamble: [],
    breakdown: [],
    didWell: [],
    missed: [],
    nextSteps: [],
    safety: [],
  };

  for (const rawLine of markdown.split(/\r?\n/)) {
    const key = headingKey(rawLine);
    if (key) {
      current = key;
      continue;
    }
    // Drop horizontal rules and the top-line score (rendered separately).
    if (/^\s*-{3,}\s*$/.test(rawLine)) continue;
    if (current === "preamble" && /overall score:/i.test(rawLine)) continue;
    buffers[current].push(rawLine);
  }

  for (const key of Object.keys(buffers) as Array<SectionKey | "preamble">) {
    sections[key] = buffers[key].join("\n").trim();
  }

  return sections;
}

/**
 * Heuristic: did the assessor say the learner missed the time-critical
 * cardiac emergency? Used to colour the Safety Assessment panel red.
 */
export function safetyLooksMissed(safetyText: string): boolean {
  if (!safetyText) return false;
  const negative =
    /\b(did not|didn['’]t|failed to|fail(?:s|ed)? to|no evidence|not (?:clearly |explicitly |adequately )?(?:recogni[sz]e[d]?|identif(?:y|ied)|escalate[d]?|treat(?:ed)?|acknowledge[d]?|appreciate[d]?)|unrecogni[sz]ed|missed|overlooked|was not (?:recogni[sz]ed|identified|escalated)|not been (?:recogni[sz]ed|identified))\b/i;
  return negative.test(safetyText);
}
