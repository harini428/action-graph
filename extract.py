import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=60,
    max_retries=1,
)

model_1 = [
    
    "openai/gpt-oss-20b",
    "nvidia/nemotron-3.5-bolt-e4b"
]


ALLOWED_TYPES = {"action_item", "decision", "decision_pending", "risk"}

SYSTEM_PROMPT = (
    "You extract decisions, action items, and risks from meeting transcripts. "
    "Return ONLY valid JSON like: "
    '{"items":[{"type":"action_item|decision|decision_pending|risk",'
    '"task":"...","owner":"...","deadline":"...","needs_review":true|false}]}. '
    "Use only what is said in the transcript. "
    "If the owner or deadline is not mentioned, write 'unknown'. Never guess. "
    "Item types: "
    "action_item = a task someone must do or is asked to do. "
    "decision = a choice the group has already made. "
    "decision_pending = a choice that still has to be made. "
    "risk = a worry or possible problem. "
    "A task that has a date is still an action_item, not a decision. "
    "Return each distinct item only once. Do not invent, split, or duplicate items. "
    "Deadline rules: "
    "A deadline must be a specific day, date, or time period (for example 'Friday', 'next week'). "
    "Vague words like 'soon', 'later', 'ASAP' are NOT deadlines: write 'unknown'. "
    "For an action_item, the deadline is when the task must be done. "
    "For a decision_pending, the deadline is when the decision must be made. "
    "For a decision or a risk, the deadline is 'unknown' unless a due date is stated. "
    "Owner rules: "
    "Name an owner only when the transcript explicitly assigns the task to that person, "
    "or the person says they will do it. "
    "Merely mentioning a task does not make the speaker its owner. "
    "A decision has no owner: write 'unknown'. "
    "If someone is assigned to handle a risk, make them the owner of that risk "
    "and do not create a separate action_item for it. "
    "Small talk and acknowledgements ('okay', 'sounds good') are not items."
    "if the sound was not decided you write what they exactly said in that transcripts"
    "source_quote must be the exact words from the transcript that this item is based on. "
    "Copy them exactly, do not rephrase. "
    "If the owner or deadline is unclear, still write 'unknown' in those fields and keep the original words in source_quote."
)
FEW_SHOT = [
    {"role": "user",
     "content": "Transcript: Priya: I will finish the API design doc by Friday."},
    {"role": "assistant",
     "content": '{"items":[{"type":"action_item","task":"Finish API design doc","owner":"Priya","deadline":"Friday","needs_review":false,"source_quote":"I will finish the API design doc by Friday."}]}'},

    {"role": "user",
     "content": "Transcript: Ravi: We decided to use React. Kumar: Server cost may go up. Ravi: Someone should update the doc soon."},
    {"role": "assistant",
     "content": '{"items":[{"type":"decision","task":"Use React for frontend","owner":"unknown","deadline":"unknown","needs_review":false,"source_quote":"We decided to use React."},{"type":"risk","task":"Server cost may go up","owner":"unknown","deadline":"unknown","needs_review":true,"source_quote":"Server cost may go up."},{"type":"action_item","task":"Update the doc","owner":"unknown","deadline":"unknown","needs_review":true,"source_quote":"Someone should update the doc soon."}]}'},

    {"role": "user",
     "content": "Transcript: Meena: Are the slides ready? Arun: Not yet, I will finish them. Meena: When? Arun: Not sure, but I will do it."},
    {"role": "assistant",
     "content": '{"items":[{"type":"action_item","task":"Finish the slides","owner":"Arun","deadline":"unknown","needs_review":true,"source_quote":"Not sure, but I will do it."}]}'},
]
    

def clean_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    return raw


def check_items(items):
    for it in items:
        if it.get("type") not in ALLOWED_TYPES:
            it["type"] = "unknown"
            it["needs_review"] = True
        if it.get("type") in ("action_item", "decision_pending"):
            if it.get("owner", "unknown") == "unknown" or it.get("deadline", "unknown") == "unknown":
                it["needs_review"] = True
    return items


def extract_items(transcript_text):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += FEW_SHOT
    messages.append({"role": "user", "content": "Transcript: " + transcript_text})

    last_error = None
    for model in model_1:
        try:
            response = client.chat.completions.create(
                model= model, 
                messages=messages,
                temperature=0,
                max_tokens=3000,
            )
            choice = response.choices[0]
            if choice.finish_reason == "length":
                raise ValueError("Output cut aachu")
            if choice.message.content is None:
                raise ValueError("Model returned no content")

            data = json.loads(clean_json(choice.message.content))
            print("Used model:", model)
            return check_items(data["items"])
        except Exception as e:
            print("FAILED:", model, "|", type(e).__name__)
            last_error = e

    raise RuntimeError("All models failed") from last_error


if __name__ == "__main__":
    with open("transcript.txt", "r", encoding="utf-8") as f:
        text = f.read()
    for item in extract_items(text):
        print(item["type"], "|", item["task"], "|", item["owner"], "|", item["deadline"])