import requests

def generate_with_ollama(model: str, prompt: str, temperature: float = 0.0) -> str:
    """
    Calls a local Ollama model.

    Requirements:
        ollama serve
        ollama pull qwen2.5:7b
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is installed and running."
        ) from exc

    return response.json().get("response", "")
