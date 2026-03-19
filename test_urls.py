import requests

token = "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"
headers = {"Authorization": f"Bearer {token}"}
payload = {"inputs": "Hi"}
urls = [
    "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    "https://router.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    "https://router.huggingface.co/hf-inference/models/HuggingFaceH4/zephyr-7b-beta",
    "https://api-inference.huggingface.co/pipeline/text-generation/HuggingFaceH4/zephyr-7b-beta"
]

for u in urls:
    res = requests.post(u, headers=headers, json=payload)
    print(f"URL: {u}")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:100]}\n")
