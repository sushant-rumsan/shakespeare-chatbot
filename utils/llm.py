import requests

from utils.config import OLLAMA_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT, OLLAMA_URL


def generate(prompt, temperature=None, timeout=None):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
                if temperature is not None
                else OLLAMA_TEMPERATURE
            },
        },
        timeout=timeout or OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["response"].strip()
