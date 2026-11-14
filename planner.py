"""PLANEJADOR: decide SE e COMO buscar, usando a memória do usuário.

Recebe a pergunta + as memórias e devolve:
  {"rota": "memoria" | "web" | "ambos",
   "motivo": "...",
   "consultas_web": ["consulta reescrita com o contexto do usuário", ...]}
"""
import json
import re

import config
from llm import chat

ROTAS = {"memoria", "web", "ambos"}
ROTA_DO_MODELO = {"memory": "memoria", "web": "web", "both": "ambos"}

SYSTEM = """You are the search planner of a personal assistant.
You receive the user's QUESTION and MEMORIES (facts we already know about this user).
Decide where the answer must come from:
- "memory": the memories alone fully answer it (personal facts, preferences, plans). No web search.
- "web": it needs current facts about the world and the memories add nothing useful.
- "both": it needs current web facts AND the memories change what to look for
  (location, diet, budget, schedule, tastes...).

For "web" or "both", write exactly 1 web search query in English,
REWRITTEN with the relevant memory details so results are personalized.
Example: question "good restaurants?" + memories "vegetarian", "in Sunnyvale",
"budget up to $30" -> "vegetarian restaurants in Sunnyvale CA under $30".
For "memory", web_queries must be [].

Always write "reason" in English.

Answer ONLY with JSON:
{"route": "memory|web|both", "reason": "<one short sentence>", "web_queries": ["..."]}"""


def _extrair_json(texto: str) -> dict:
    """Tenta ler o JSON mesmo se o modelo colocar texto ou ``` em volta."""
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        achado = re.search(r"\{.*\}", texto, re.DOTALL)
        if not achado:
            raise
        return json.loads(achado.group(0))


def planejar(pergunta: str, memorias: list[dict]) -> dict:
    lista = "\n".join(f"- {m['texto']}" for m in memorias) or "(none)"
    user = f"QUESTION: {pergunta}\n\nMEMORIES:\n{lista}"

    try:
        plano = _extrair_json(chat(config.PLANNER_MODEL, SYSTEM, user, json_mode=True))
        # O modelo responde em inglês; traduzimos para os nomes internos.
        rota = ROTA_DO_MODELO.get(str(plano.get("route", "")).strip().lower(), "")
        if rota not in ROTAS:
            raise ValueError(f"rota inválida: {rota!r}")
        consultas = [c for c in plano.get("web_queries", []) if isinstance(c, str) and c.strip()]
        if rota != "memoria" and not consultas:
            consultas = [pergunta]  # precisa buscar mas não veio consulta: usa a pergunta
        if rota == "memoria":
            consultas = []
        return {"rota": rota, "motivo": plano.get("reason", ""),
                "consultas_web": consultas[:1], "fallback": False}
    except Exception as erro:
        # FALLBACK: se algo der errado, busca em tudo. A demo nunca trava.
        return {"rota": "ambos", "motivo": f"Fallback ({type(erro).__name__}): searching everything.",
                "consultas_web": [pergunta], "fallback": True}
