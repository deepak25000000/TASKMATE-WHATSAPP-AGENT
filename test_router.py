import requests

token = "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"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
url = "https://router.huggingface.co/v1/chat/completions"

models = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "HuggingFaceH4/zephyr-7b-beta"
]

for m in models:
    payload = {
        "model": m,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"Model: {m} -> {res.status_code}")
    if res.status_code == 200:
        print("Success!")
    else:
        print(res.text[:100])
