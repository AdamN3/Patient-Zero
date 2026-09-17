import re
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

PATIENT_SYSTEM = """You are a standardized patient in a medical training simulation.
You are role-playing a patient. You are NOT an assistant and NEVER give medical advice.

HIDDEN CASE FILE (never state the diagnosis; reveal details only when the student asks):
- Persona: 54-year-old store manager, anxious but cooperative. Came straight from work.
- Presenting complaint: pressure in the chest for about 2 hours.
- History if asked: heavy central chest pressure, spreads to the left arm and jaw;
  started while climbing stairs; short of breath; sweaty; mildly nauseated;
  constant since it began; 7/10; nothing has helped.
- Risk factors if asked: smokes ~15/day for 30 years; father had a heart attack at 60;
  no known conditions; on no medications.
- Hidden diagnosis (NEVER reveal): acute coronary syndrome.

RULES:
- Output spoken words only. Never include stage directions, actions, or text in asterisks.
- Stay fully in character. Answer as this patient would, in plain, non-medical language.
- Only share information the student specifically asks about.
- Do not volunteer the whole story.
- Show realistic worry. Keep answers to 1-3 sentences.
- If the student asks what's wrong or asks for a diagnosis, respond as a scared
  patient would ("I don't know, that's why I'm here"), never as a clinician.
"""

FEEDBACK_SYSTEM = """You are a medical education assessor grading a simulated
clinical interview. This is educational feedback, not real-world medical advice.

The hidden case is acute coronary syndrome in a 54-year-old patient.

Score only questions, statements, and actions explicitly present in the transcript.
Do not award credit simply because the patient mentioned something.

Use this 100-point rubric:
- Communication and empathy: 10 points
- Chest-pain history (onset, site, character, radiation, severity, timing,
  triggers and relieving factors): 25 points
- Associated symptoms and red flags: 15 points
- Cardiovascular risk factors: 15 points
- Medical history, medications, and allergies: 10 points
- Clinical reasoning, recognition of urgency, and immediate plan: 25 points

This is formative feedback for a simulation. Use a calm, supportive teaching tone.
Do not make claims about whether the learner is fit for unsupervised clinical practice.
Do not provide medication doses or detailed treatment protocols.
When escalation is needed, recommend urgent assessment, senior help, an ECG,
monitoring, and following the applicable local emergency protocol.

Return the report in exactly this general structure:

OVERALL SCORE: [score]/100

SCORE BREAKDOWN
- Communication and empathy: [score]/10
- Chest-pain history: [score]/25
- Associated symptoms and red flags: [score]/15
- Cardiovascular risk factors: [score]/15
- Medical history, medications, and allergies: [score]/10
- Clinical reasoning and immediate plan: [score]/25

WHAT YOU DID WELL
- Give specific examples from the transcript.

WHAT YOU MISSED
- Identify important questions or actions that were absent.

TOP 3 NEXT STEPS
1. Give the three most important improvements.

SAFETY ASSESSMENT
State whether the learner recognized a possible time-critical cardiac emergency
and proposed appropriate immediate escalation.

Be concise, supportive, and specific. Never invent something the learner did.
Make sure the category scores add up to the overall score.
"""


def make_transcript(messages):
    lines = []

    for message in messages:
        if message["role"] == "user":
            speaker = "Student"
        else:
            speaker = "Patient"

        text_parts = []

        for content in message["content"]:
            if "text" in content:
                text_parts.append(content["text"])

        lines.append(f"{speaker}: {' '.join(text_parts)}")

    return "\n".join(lines)

def correct_total_score(feedback):
    score_pattern = r"^- [^:\n]+:\s*(\d+)/(?:10|15|25)\b"
    category_scores = re.findall(
        score_pattern,
        feedback,
        flags=re.MULTILINE,
    )

    if len(category_scores) == 6:
        correct_total = sum(int(score) for score in category_scores)

        feedback = re.sub(
            r"OVERALL SCORE:\s*\d+/100",
            f"OVERALL SCORE: {correct_total}/100",
            feedback,
            count=1,
        )

    return feedback

def generate_feedback(messages, clinical_impression):
    transcript = make_transcript(messages)

    assessment_request = f"""Assess the following completed simulation.

<transcript>
{transcript}
</transcript>

The learner's final clinical impression and immediate plan were:

<clinical_impression>
{clinical_impression}
</clinical_impression>
"""

    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": FEEDBACK_SYSTEM}],
        messages=[
            {
                "role": "user",
                "content": [{"text": assessment_request}],
            }
        ],
        inferenceConfig={"maxTokens": 1200, "temperature": 0.2},
    )

    feedback = response["output"]["message"]["content"][0]["text"]
    return correct_total_score(feedback)


messages = []

print("You are the clinician. Interview the patient.")
print("Type 'done' for feedback or 'quit' to leave without feedback.\n")

while True:
    student = input("You: ").strip()

    if student.lower() == "quit":
        print("Session ended without feedback.")
        break

    if student.lower() == "done":
        if not messages:
            print("Ask the patient at least one question first.\n")
            continue

        print("\nBefore receiving feedback, give your working diagnosis")
        print("and describe what you would do immediately.")
        clinical_impression = input("Your assessment and plan: ").strip()

        print("\nGenerating your feedback...\n")

        feedback = generate_feedback(messages, clinical_impression)

        print("=" * 60)
        print("INTERVIEW FEEDBACK")
        print("=" * 60)
        print(feedback)
        break

    if not student:
        continue

    messages.append(
        {
            "role": "user",
            "content": [{"text": student}],
        }
    )

    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": PATIENT_SYSTEM}],
        messages=messages,
        inferenceConfig={"maxTokens": 300, "temperature": 0.7},
    )

    reply = response["output"]["message"]
    messages.append(reply)

    print("Patient:", reply["content"][0]["text"], "\n")