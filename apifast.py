import os, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=30,
    max_retries=0,
)

models = [
    "z-ai/glm-5.3-flash",
    "deepseek-ai/deepseek-v4.1-flash",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "minimaxai/minimax-m3.1-flash",
    "nvidia/nemotron-3.5-bolt-e4b",
    "openai/gpt-oss-20b",
    "google/gemma-4-31b-it",
    "z-ai/glm-5.3",
]

for m in models:
    t = time.time()
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": 'Return only this JSON: {"ok": true}'}],
            max_tokens=100,
        )
        c = r.choices[0].message.content
        print(f"{time.time()-t:5.1f}s OK   {m} | content={c!r}"[:140])
    except Exception as e:
        print(f"{time.time()-t:5.1f}s FAIL {m} | {type(e).__name__}")