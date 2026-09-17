/**
 * Typed client for the Patient Zero Flask API (backend/app.py).
 *
 * The backend is stateless: the browser owns the conversation and sends the
 * full Bedrock `messages` array on every request.
 */

export const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000"
).replace(/\/+$/, "");

// ---------------------------------------------------------------------------
// Bedrock Converse message shape (what /api/chat and /api/feedback expect)
// ---------------------------------------------------------------------------

export type BedrockRole = "user" | "assistant";

/** A single content block. Bedrock Converse uses `{ text }` with no `type` key. */
export interface BedrockTextBlock {
  text: string;
}

export interface BedrockMessage {
  role: BedrockRole;
  content: BedrockTextBlock[];
}

export function userMessage(text: string): BedrockMessage {
  return { role: "user", content: [{ text }] };
}

export function messageText(message: BedrockMessage): string {
  return message.content
    .map((block) => block.text ?? "")
    .join(" ")
    .trim();
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

export interface HealthResponse {
  ok: boolean;
  model: string;
  region: string;
}

export interface Variant {
  id: string;
  label: string;
  demographics: string;
}

export interface ChatResponse {
  guardrail: boolean;
  text: string;
  /** Raw Bedrock assistant message — append this to the local history. */
  message: BedrockMessage;
  audio_base64: string | null;
  audio_error?: string | null;
}

export interface BreakdownRow {
  category: string;
  score: number | null;
  max: number;
}

export interface FeedbackResponse {
  feedback_markdown: string;
  overall_score: number | null;
  breakdown: BreakdownRow[];
  truncated: boolean;
}

export interface EquityResponse {
  highest: { variant: string; score: number } | null;
  lowest: { variant: string; score: number } | null;
  gap: number | null;
  message: string;
}

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/** Turn any thrown value into a human-readable banner message. */
export function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    const prefix =
      error.status === 503
        ? "Backend unavailable"
        : error.status === 502
          ? "AWS Bedrock error"
          : error.status === 400
            ? "Invalid request"
            : `Error ${error.status}`;
    return error.code
      ? `${prefix} (${error.code}): ${error.message}`
      : `${prefix}: ${error.message}`;
  }
  if (error instanceof TypeError) {
    // fetch() throws TypeError on network failure / CORS block.
    return `Cannot reach the backend at ${API_BASE}. Is the Flask server running?`;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(init?.headers ?? {}),
    },
  });

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    // Non-JSON body (e.g. a proxy error page). Fall through to status check.
  }

  if (!response.ok) {
    const body = (payload ?? {}) as { error?: string; code?: string };
    throw new ApiError(
      body.error ?? response.statusText ?? "Request failed",
      response.status,
      body.code,
    );
  }

  return payload as T;
}

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

export function getVariants(): Promise<Variant[]> {
  return request<Variant[]>("/api/variants");
}

export function postChat(body: {
  variant: string;
  messages: BedrockMessage[];
  voice: boolean;
}): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function postFeedback(body: {
  messages: BedrockMessage[];
  clinical_impression: string;
}): Promise<FeedbackResponse> {
  return request<FeedbackResponse>("/api/feedback", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function postEquity(scores: Record<string, number>): Promise<EquityResponse> {
  return request<EquityResponse>("/api/equity", {
    method: "POST",
    body: JSON.stringify({ scores }),
  });
}
