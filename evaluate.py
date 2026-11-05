import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import extract

load_dotenv()
extract.MODELS = ["openai/gpt-oss-20b"]            # evaluation-ku oru model mattum
extract.client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=120,
    max_retries=3,
)
from extract import extract_items


def norm(s):
    s = str(s).lower().strip().rstrip(".")
    for prefix in ("the ", "on ", "by "):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s


with open("data/answer.json", encoding="utf-8") as f:
    answers = json.load(f)

correct = total = 0
failed = []

for tid, expected in answers.items():
    path = f"data/{tid}.txt"
    if not os.path.exists(path):
        print(f"\n{tid}: SKIPPED (file illa)")
        continue

    with open(path, encoding="utf-8") as f:
        text = f.read()

    try:
        got = extract_items(text)
    except Exception as e:
        print(f"\n{tid}: LLM FAILED ({type(e).__name__}), skipped")
        failed.append(tid)
        continue

    used = set()
    print(f"\n{tid}: expected {len(expected)} items, got {len(got)}")

    for exp in expected:
        match = None
        for i, g in enumerate(got):
            if i in used:
                continue
            if g.get("type") == exp["type"] and exp["keyword"].lower() in g.get("task", "").lower():
                match = i
                break

        total += 3
        if match is None:
            print(f"  MISSING item: {exp['type']} / {exp['keyword']}")
            continue

        used.add(match)
        g = got[match]
        correct += 1
        for fld in ("owner", "deadline"):
            if norm(g.get(fld, "")) == norm(exp[fld]):
                correct += 1
            else:
                print(f"  MISS {fld} ({exp['keyword']}): expected {exp[fld]!r}, got {g.get(fld)!r}")

    for i, g in enumerate(got):
        if i not in used:
            total += 3
            print(f"  EXTRA item: {g.get('type')} | {g.get('task')}")

print(f"\nAccuracy: {correct}/{total} = {100 * correct / total:.0f}%" if total else "No items")
if failed:
    print("LLM failed for:", failed, "(score-la serala)")