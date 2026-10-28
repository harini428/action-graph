import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()            # .env-la irundhu API key padikkum

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=60,
    max_retries=2,
)


# 1. Transcript padi
with open("transcript.txt", "r", encoding="utf-8") as f:
    real_transcript = f.read()

# 2. Rules
SYStem_prompt = (
    "You extract decisions, action items, and risks from meeting transcripts. "
    "Return ONLY valid JSON like: "
    '{"items":[{"type":"action_item|decision|decision_pending|risk",'
    '"task":"...","owner":"...","deadline":"...","needs_review":true|false}]}. '
    "Use only what is said in the transcript. "
    "If the owner or deadline is not mentioned, write 'unknown'. Never guess."
    "A deadline must be a specific day, date, or time period given for the task "
"(for example 'Friday', 'next week'). "
"Vague words like 'soon', 'later', 'ASAP' are NOT deadlines: write 'unknown'. "
"For risks, write 'unknown' for deadline unless a due date is stated. "
)

# 3. Few-shot examples
few_shot = [{"role": "system", "content": SYStem_prompt},

    {"role": "user", "content": "Transcript: Priya: I will finish the API design doc by Friday."},
    {"role": "assistant", "content": '{"items":[{"type":"action_item","task":"Finish API design doc","owner":"Priya","deadline":"Friday","needs_review":false}]}'},

    {"role": "user", "content": "Transcript: Ravi: We decided to use React. Kumar: Server cost may go up. Ravi: Someone should update the doc soon."},
    {"role": "assistant", "content": '{"items":[{"type":"decision","task":"Use React for frontend","owner":"unknown","deadline":"unknown","needs_review":false},{"type":"risk","task":"Server cost may go up","owner":"Kumar","deadline":"unknown","needs_review":true},{"type":"action_item","task":"Update the doc","owner":"unknown","deadline":"unknown","needs_review":true}]}'},

    
    {"role": "user", "content": "Transcript: " + real_transcript},
]
def extract_items(transcript_text):
    messages = [{"role": "system", "content": SYStem_prompt}]
    messages += few_shot
    messages.append({"role": "user", "content": "Transcript: " + transcript_text})

    response = client.chat.completions.create(
        model="minimaxai/minimax-m3.1-flash",
        messages=messages,
        temperature=0,
        max_tokens=2000,
    )

    choice = response.choices[0]
    if choice.finish_reason == "length":
        raise ValueError("Output cut aachu, max_tokens kooda vai")
    print( choice.finish_reason)

    raw = choice.message.content
    if raw is None:
        raise ValueError("Model returned no content")

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()

    data = json.loads(raw)
    return data["items"]


if __name__ == "__main__":
    with open("transcript.txt", "r", encoding="utf-8") as f:
        text = f.read()

    items = extract_items(text)
    for item in items:
        print(item["type"], "|", item["task"], "|", item["owner"], "|", item["deadline"])


