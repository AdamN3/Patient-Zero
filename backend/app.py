from dotenv import load_dotenv
load_dotenv()

"""Patient Zero — Flask JSON API for the Next.js frontend.

Stateless: the client owns the conversation and sends the full Bedrock
`messages` list on every request. All model/prompt logic lives in simulation.py.
"""
import base64
import os
import re
from functools import lru_cache

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)
from flask import Flask, jsonify, request
from flask_cors import CORS

import simulation
from simulation import (
    FEEDBACK_SYSTEM,
    PATIENT_VARIANTS,
    REFERENCE_MATERIALS,
    build_patient_system,
    correct_total_score,
    create_patient_audio,
    extract_overall_score,
    generate_feedback,  # noqa: F401  (kept for parity; see assess_interview)
    make_transcript,
)


# --------------------------------------------------------------------------- #
# Config (env vars, falling back to simulation.py's hardcoded values)
# --------------------------------------------------------------------------- #

def _env(name, default):
    value = os.environ.get(name, "").strip()
    return value or default


AWS_REGION = _env("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = _env("BEDROCK_MODEL_ID", simulation.MODEL_ID)
GUARDRAIL_ID = _env("GUARDRAIL_ID", simulation.GUARDRAIL_ID)
GUARDRAIL_VERSION = _env("GUARDRAIL_VERSION", simulation.GUARDRAIL_VERSION)
POLLY_VOICE_ID = _env("POLLY_VOICE_ID", "Joanna")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
LOCAL_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

PATIENT_MAX_TOKENS = 300
PATIENT_TEMPERATURE = 0.7
FEEDBACK_MAX_TOKENS = 2500  # was 1200 in the Streamlit app; that truncated reports
FEEDBACK_TEMPERATURE = 0.2
MAX_QUESTION_CHARS = 2000
MAX_IMPRESSION_CHARS = 4000

GUARDRAIL_DECLINE_TEXT = "I'd rather not answer that."

EXPIRED_CREDENTIAL_CODES = {
    "ExpiredToken",
    "ExpiredTokenException",
    "InvalidClientTokenId",
    "UnrecognizedClientException",
    "InvalidSignatureException",
    "InvalidIdentityToken",
}

# Stable ids for the frontend ("Patient A (54, male)" -> "patient_a")
VARIANTS = [
    {
        "id": re.sub(r"[^a-z0-9]+", "_", label.split("(")[0].strip().lower()),
        "label": label,
        "demographics": demographics,
    }
    for label, demographics in PATIENT_VARIANTS.items()
]
VARIANT_LOOKUP = {v["id"]: v for v in VARIANTS}
VARIANT_LOOKUP.update({v["label"]: v for v in VARIANTS})


# --------------------------------------------------------------------------- #
# App + AWS clients
# --------------------------------------------------------------------------- #

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": LOCAL_ORIGINS + ALLOWED_ORIGINS}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@lru_cache(maxsize=1)
def bedrock():
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


@lru_cache(maxsize=1)
def polly():
    return boto3.client("polly", region_name=AWS_REGION)


def patient_audio(text):
    """Polly TTS honouring POLLY_VOICE_ID; falls back to simulation's helper."""
    if POLLY_VOICE_ID == "Joanna" and AWS_REGION == "us-east-1":
        return create_patient_audio(text)
    response = polly().synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=POLLY_VOICE_ID,
        Engine="neural",
    )
    return response["AudioStream"].read()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def error(status, message, **extra):
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status


def aws_error_response(exc):
    """Map AWS/boto failures onto HTTP: 503 for credential problems,
    400 for request validation, 502 for everything else upstream."""
    if isinstance(exc, (NoCredentialsError, PartialCredentialsError)):
        return error(503, "AWS credentials are missing on the server.", code="NoCredentials")

    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "ClientError")
        message = exc.response.get("Error", {}).get("Message", str(exc))
        if code in EXPIRED_CREDENTIAL_CODES:
            return error(503, "AWS credentials have expired; refresh them on the server.", code=code)
        if code == "ValidationException":
            return error(400, message, code=code)
        return error(502, message, code=code)

    if isinstance(exc, BotoCoreError):
        return error(502, str(exc), code=type(exc).__name__)

    raise exc


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def validate_messages(messages):
    """Return an error string, or None if `messages` is a valid Bedrock history."""
    if not isinstance(messages, list) or not messages:
        return "messages must be a non-empty list."

    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            return f"messages[{index}] must be an object."
        if message.get("role") not in ("user", "assistant"):
            return f"messages[{index}].role must be 'user' or 'assistant'."
        content = message.get("content")
        if not isinstance(content, list) or not content:
            return f"messages[{index}].content must be a non-empty list."
        for item in content:
            if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                return f"messages[{index}].content items must be {{\"text\": string}}."
            if message["role"] == "user" and len(item["text"]) > MAX_QUESTION_CHARS:
                return f"messages[{index}] text exceeds {MAX_QUESTION_CHARS} characters."

    if messages[-1]["role"] != "user":
        return "The last message must have role 'user'."

    return None


def assess_interview(messages, clinical_impression):
    """Same prompt as simulation.generate_feedback, but with a larger token
    budget (the 1200 default truncates reports) and no guardrail — the
    guardrail blocks the assessor's clinical content."""
    transcript = make_transcript(messages)

    request_text = f"""Assess this completed simulation.

<transcript>
{transcript}
</transcript>

The learner's final clinical impression and immediate plan were:

<clinical_impression>
{clinical_impression}
</clinical_impression>
"""

    response = bedrock().converse(
        modelId=BEDROCK_MODEL_ID,
        system=[{"text": FEEDBACK_SYSTEM}],
        messages=[{"role": "user", "content": [{"text": request_text}]}],
        inferenceConfig={
            "maxTokens": FEEDBACK_MAX_TOKENS,
            "temperature": FEEDBACK_TEMPERATURE,
        },
    )

    feedback = response["output"]["message"]["content"][0]["text"]
    return correct_total_score(feedback), response.get("stopReason")


BREAKDOWN_CATEGORIES = [
    ("Pain characterisation", 20),
    ("Associated symptoms and red flags", 20),
    ("Cardiovascular risk factors", 15),
    ("Relevant medical and social background", 10),
    ("Patient perspective and communication", 10),
    ("Clinical reasoning and safety", 25),
]


def parse_breakdown(feedback):
    """Pull the six category scores out of the report. Tolerates the model
    wrapping headings in markdown ("**Pain characterisation: 7/20**",
    "- Pain characterisation: 7/20", "### Pain characterisation — 7/20")."""
    breakdown = []
    for category, maximum in BREAKDOWN_CATEGORIES:
        pattern = (
            r"^[\s\-\*#>]*" + re.escape(category)
            + r"\s*[:\-–—]?\s*\**\s*(\d{1,3})\s*/\s*" + str(maximum) + r"\b"
        )
        match = re.search(pattern, feedback, flags=re.MULTILINE | re.IGNORECASE)
        score = int(match.group(1)) if match else None
        if score is not None:
            score = max(0, min(score, maximum))
        breakdown.append({"category": category, "score": score, "max": maximum})
    return breakdown


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.get("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "model": BEDROCK_MODEL_ID,
            "region": AWS_REGION,
            "guardrail": {"id": GUARDRAIL_ID, "version": GUARDRAIL_VERSION},
            "voice": POLLY_VOICE_ID,
            "references_loaded": sorted(REFERENCE_MATERIALS.keys()),
        }
    )


@app.get("/api/variants")
def variants():
    return jsonify(VARIANTS)


@app.post("/api/chat")
def chat():
    body = json_body()
    if body is None:
        return error(400, "Request body must be JSON.")

    variant = VARIANT_LOOKUP.get(body.get("variant"))
    if variant is None:
        return error(
            400,
            "Unknown variant.",
            allowed=[v["id"] for v in VARIANTS],
        )

    messages = body.get("messages")
    problem = validate_messages(messages)
    if problem:
        return error(400, problem)

    want_voice = bool(body.get("voice", False))

    try:
        response = bedrock().converse(
            modelId=BEDROCK_MODEL_ID,
            system=[{"text": build_patient_system(variant["demographics"])}],
            messages=messages,
            inferenceConfig={
                "maxTokens": PATIENT_MAX_TOKENS,
                "temperature": PATIENT_TEMPERATURE,
            },
            guardrailConfig={
                "guardrailIdentifier": GUARDRAIL_ID,
                "guardrailVersion": GUARDRAIL_VERSION,
            },
        )
    except (ClientError, BotoCoreError) as exc:
        return aws_error_response(exc)

    if response.get("stopReason") == "guardrail_intervened":
        return jsonify(
            {
                "guardrail": True,
                "text": GUARDRAIL_DECLINE_TEXT,
                "message": {
                    "role": "assistant",
                    "content": [{"text": GUARDRAIL_DECLINE_TEXT}],
                },
                "audio_base64": None,
            }
        )

    reply = response["output"]["message"]
    text = " ".join(
        item["text"] for item in reply.get("content", []) if "text" in item
    ).strip()

    audio_base64 = None
    audio_error = None
    if want_voice and text:
        try:
            audio_base64 = base64.b64encode(patient_audio(text)).decode("ascii")
        except (ClientError, BotoCoreError) as exc:
            # Voice is best-effort: fall back to text only, like the Streamlit app.
            audio_error = str(exc)

    return jsonify(
        {
            "guardrail": False,
            "text": text,
            "message": reply,  # append this to `messages` on the client
            "audio_base64": audio_base64,
            "audio_error": audio_error,
        }
    )


@app.post("/api/feedback")
def feedback():
    body = json_body()
    if body is None:
        return error(400, "Request body must be JSON.")

    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return error(400, "messages must be a non-empty list.")
    for index, message in enumerate(messages):
        if (
            not isinstance(message, dict)
            or message.get("role") not in ("user", "assistant")
            or not isinstance(message.get("content"), list)
        ):
            return error(400, f"messages[{index}] is not a valid Bedrock message.")
    if not any(m["role"] == "user" for m in messages):
        return error(400, "Ask the patient at least one question before requesting feedback.")

    clinical_impression = body.get("clinical_impression")
    if not isinstance(clinical_impression, str) or not clinical_impression.strip():
        return error(400, "clinical_impression must be a non-empty string.")
    if len(clinical_impression) > MAX_IMPRESSION_CHARS:
        return error(400, f"clinical_impression exceeds {MAX_IMPRESSION_CHARS} characters.")

    try:
        feedback_markdown, stop_reason = assess_interview(
            messages, clinical_impression.strip()
        )
    except (ClientError, BotoCoreError) as exc:
        return aws_error_response(exc)

    breakdown = parse_breakdown(feedback_markdown)
    overall_score = extract_overall_score(feedback_markdown)

    # If all six categories parsed, the sum is authoritative (the model's own
    # arithmetic is unreliable). Keep the markdown consistent with it.
    if all(item["score"] is not None for item in breakdown):
        total = sum(item["score"] for item in breakdown)
        if overall_score != total:
            overall_score = total
            feedback_markdown = re.sub(
                r"OVERALL SCORE:\s*\d+/100",
                f"OVERALL SCORE: {total}/100",
                feedback_markdown,
                count=1,
            )

    return jsonify(
        {
            "feedback_markdown": feedback_markdown,
            "overall_score": overall_score,
            "breakdown": breakdown,
            "truncated": stop_reason == "max_tokens",
        }
    )


@app.post("/api/equity")
def equity():
    body = json_body()
    if body is None:
        return error(400, "Request body must be JSON.")

    scores = body.get("scores")
    if not isinstance(scores, dict) or not scores:
        return error(400, "scores must be a non-empty object of {variant: score}.")

    clean = {}
    for variant, score in scores.items():
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            return error(400, f"Score for '{variant}' must be a number.")
        clean[str(variant)] = int(round(score))

    if len(clean) < 2:
        return jsonify(
            {
                "highest": None,
                "lowest": None,
                "gap": None,
                "message": (
                    "Interview the same case as two or more patient variants, "
                    "finishing each, to compare your scores."
                ),
            }
        )

    highest_variant = max(clean, key=clean.get)
    lowest_variant = min(clean, key=clean.get)
    highest = clean[highest_variant]
    lowest = clean[lowest_variant]
    gap = highest - lowest

    if gap == 0:
        message = "No score gap across variants — same case, same performance."
    else:
        message = (
            f"Score gap of {gap} points across variants. "
            "Same case, same medicine — a gap is a signal to reflect on, "
            "not a verdict."
        )

    return jsonify(
        {
            "highest": {"variant": highest_variant, "score": highest},
            "lowest": {"variant": lowest_variant, "score": lowest},
            "gap": gap,
            "message": message,
        }
    )


@app.errorhandler(404)
def not_found(_):
    return error(404, "Not found.")


@app.errorhandler(405)
def method_not_allowed(_):
    return error(405, "Method not allowed.")


@app.errorhandler(500)
def internal_error(_):
    return error(500, "Internal server error.")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
