import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    timeout=60,
    max_retries=3,
)

candidates = [
    "mistralai/mistral-large-2-instruct",
    "nvidia/llama-3.1-nemotron-51b-instruct",
    "nv-mistralai/mistral-nemo-12b-instruct",
    "mistralai/mistral-7b-instruct-v0.3",
    "microsoft/phi-3.5-moe-instruct",
]

for model in candidates:
    try:
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hi"}],
            max_tokens=5,
            
)
        
        print("WORKS :", model)
    except Exception as e:
        print("FAILED:", model, "|", str(e)[:60])