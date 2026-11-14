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


def buscar_memoria(pergunta: str, user_id: str, top_k: int = 10) -> list[dict]:
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
        auto_routing="accuracy",  # a Telem escolhe os melhores buscadores...
        providers_include=config.TELEM_PROVIDERS,  # ...mas só entre estes (FinOps)
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
        "topico": roteamento[0].get("topic") if roteamento else None,
        "buscadores": [
            {"nome": run.provider, "status": run.status,
             "latencia_ms": run.latency_ms, "n_resultados": len(run.results)}
            for run in resp.by_provider
        ],
    }
    return {"resultados": resultados, "metadados": metadados}


def extrair_paginas(urls: list[str]) -> list[dict]:
    """Usa a Tavily para baixar o texto limpo (markdown) de algumas páginas."""
    # timeout curto: sites que bloqueiam robôs (Yelp, OpenTable) não travam a demo
    resp = tavily.extract(urls=urls, format="markdown", extract_depth="basic", timeout=10)
    return [
        {"url": p["url"], "conteudo": p.get("raw_content") or ""}
        for p in resp.get("results", [])
    ]


# ---------------- Telem Monitors: acompanhar uma consulta personalizada ----------------
# Custo: cada execução do monitor é cobrada. Por isso: a cada 6h e expira em 2 dias
# (~8 execuções). O botão "Stop" na tela apaga o monitor antes disso.
MONITOR_FREQUENCIA = "6h"
MONITOR_DURACAO = "2d"


def _monitor_info(m) -> dict:
    return {
        "id": m.id,
        "consulta": m.query,
        "status": m.status,
        "frequencia": m.frequency,
        "expira_em": m.expires_at,
        "agente": m.agent_state.status if m.agent_state else None,
    }


def criar_monitor(consulta: str) -> dict:
    """Cria um Telem Monitor que repete a busca e guarda o que mudar."""
    m = telem.monitors.create(consulta, frequency=MONITOR_FREQUENCIA, ttl=MONITOR_DURACAO)
    return _monitor_info(m)


def ver_monitor(monitor_id: str) -> dict:
    return _monitor_info(telem.monitors.get(monitor_id))


def parar_monitor(monitor_id: str) -> None:
    telem.monitors.delete(monitor_id)
