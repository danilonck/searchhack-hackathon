"""Cliente do LLM: o SDK da OpenAI apontado para o OpenRouter."""
import os

import config  # noqa: F401  (carrega o .env)
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)


def chat(model: str, system: str, user: str, json_mode: bool = False) -> str:
    """Faz uma chamada ao modelo e devolve só o texto da resposta."""
    extra = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
        **extra,
    )
    return resp.choices[0].message.content or ""
