from core.config import get_settings
from openai import OpenAI
import ollama
import requests

def generate_answer(prompt: str) -> str:
    settings = get_settings()

    # -----------------------
    # 1) CUSTOM INTERNAL PROVIDER
    # -----------------------
    if settings.LLM_PROVIDER == "custom":
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.CUSTOM_LLM_TOKEN}"
        }

        payload = {
            "model": settings.CUSTOM_LLM_MODEL,
            "messages": [
                {
                    "role": "developer",
                    "content": "You are an AI assistant that follows instructions extremely well."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "seed": 42,
            "n": 1
        }

        try:
            response = requests.post(
                settings.CUSTOM_LLM_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            # Format jawaban dari API Qwen-like
            # Biasanya berada di bagian: choices[0].message.content
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            raise Exception(f"Custom LLM error: {e}")

    # -----------------------
    # 2) OLLAMA LOCAL
    # -----------------------
    if settings.LLM_PROVIDER == "ollama":
        response = ollama.chat(model="llama3", messages=[
            {"role": "user", "content": prompt}
        ])
        return response["message"]["content"]

    # -----------------------
    # 3) OPENAI API DEFAULT
    # -----------------------
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Kamu adalah asisten AI yang menjawab berdasarkan konteks dokumen."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()
