import os, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
)

skip = ["embed", "rerank", "guard", "safety", "translate", "vision",
        "vl", "code", "reward", "clip", "parse", "topic", "riva"]

ids = [m.id for m in client.models.list()]
ids = [i for i in ids if not any(w in i.lower() for w in skip)]
print("Trying", len(ids), "models...")

for model in ids[:60]:
    try:
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hi"}],
            max_tokens=5,
        )
        print("WORKS :", model)
    except Exception as e:
        pass
    time.sleep(1.6)   # free limit ~40 requests per minute
print("Done")