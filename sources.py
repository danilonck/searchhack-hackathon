"""As três fontes de dados: Mem0 (memória), Telem (busca web) e Tavily (extração)."""
import os

import config  # noqa: F401  (carrega o .env antes do mem0)
from mem0 import MemoryClient
from tavily import TavilyClient
from telem import Telem

# Um cliente de cada serviço. Cada um lê a chave do ambiente.
mem0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
telem = Telem(api_key=os.environ["TELEM_API_KEY"])


def buscar_memoria(pergunta: str, user_id: str, top_k: int = 5) -> list[dict]:
    """Busca no Mem0 as memórias deste usuário mais parecidas com a pergunta.

    Atenção: na busca, o usuário vai dentro de `filters` (o SDK rejeita user_id solto).
    """
    resposta = mem0.search(pergunta, filters={"user_id": user_id}, top_k=top_k)
    return [
        {"texto": m["memory"], "score": m.get("score")}
        for m in resposta.get("results", [])
    ]


def buscar_web(consulta: str, num_results: int = 5) -> dict:
    """Busca na web pela Telem, deixando o auto-roteamento escolher os buscadores."""
    resp = telem.search(
        consulta,
        auto_routing="accuracy",
        max_routing_providers=3,  # no máximo 3 buscadores: menos custo
        num_results=num_results,
    )

    # Junta os resultados de todos os buscadores e remove URLs repetidas.
    vistos, resultados = set(), []
    for r in resp.results:
        if r.url in vistos:
            continue
        vistos.add(r.url)
        resultados.append({
            "titulo": r.title,
            "url": r.url,
            "trecho": r.content,
            "buscador": r.provider,
        })

    # Metadados para mostrar na tela.
    roteamento = resp.raw.get("routing") or []
    metadados = {
        "interaction_id": resp.interaction_id,
        "status": resp.status,
        "escolhidos": roteamento[0].get("providers", []) if roteamento else [],
        "buscadores": [
            {"nome": run.provider, "status": run.status,
             "latencia_ms": run.latency_ms, "n_resultados": len(run.results)}
            for run in resp.by_provider
        ],
    }
    return {"resultados": resultados, "metadados": metadados}


def extrair_paginas(urls: list[str]) -> list[dict]:
    """Usa a Tavily para baixar o texto limpo (markdown) de algumas páginas."""
    resp = tavily.extract(urls=urls, format="markdown", extract_depth="basic")
    return [
        {"url": p["url"], "conteudo": p.get("raw_content") or ""}
        for p in resp.get("results", [])
    ]
