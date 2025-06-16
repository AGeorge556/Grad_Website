import os
import requests
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
groq_api_key = os.getenv("GROQ_API_KEY")

def groq_chat(message: str) -> str:
    try:
        print("[DEBUG] Sending message to Groq:", message, flush=True)
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are an AI tutor who helps students learn effectively. You provide clear, concise explanations and can help with various subjects. You're knowledgeable but also engaging and encouraging. When appropriate, you can break down complex topics into simpler parts and provide examples to illustrate concepts."},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
        )
        response.raise_for_status()
        data = response.json()
        print("[DEBUG] Groq response:", data, flush=True)
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[DEBUG] Groq chat error: {e}", flush=True)
        logger.error(f"Groq chat error: {e}")
        return "Sorry, I couldn't answer that question right now." 