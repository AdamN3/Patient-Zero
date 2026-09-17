import boto3


polly = boto3.client("polly", region_name="us-east-1")

response = polly.synthesize_speech(
    Text=(
        "I've had this pressure in my chest for a couple of hours, "
        "and it won't go away."
    ),
    OutputFormat="mp3",
    VoiceId="Joanna",
    Engine="neural",
)

with open("polly_test.mp3", "wb") as audio_file:
    audio_file.write(response["AudioStream"].read())

print("Success: created polly_test.mp3")