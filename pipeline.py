"""Junta tudo: memória -> planejador -> (Telem + Tavily) -> combinador."""
import time

import sources
from combiner import responder
from planner import planejar

# Custos ESTIMADOS (tabela de preços da Telem: ~US$0,005 por buscador consultado).
CUSTO_POR_BUSCADOR_USD = 0.005
BUSCADORES_TIPICOS = 7          # o auto-roteamento da Telem costuma escolher ~7
CUSTO_EXTRACAO_USD = 0.003      # estimativa (Tavily extract basic, 3 páginas)
CUSTO_BUSCA_EVITADA_USD = BUSCADORES_TIPICOS * CUSTO_POR_BUSCADOR_USD + CUSTO_EXTRACAO_USD

N_PAGINAS_EXTRAIR = 3


def executar(pergunta: str, user_id: str) -> dict:
    t0 = time.time()
    tempos = {}

    # 1. Memória do usuário
    memorias = sources.buscar_memoria(pergunta, user_id)
    tempos["memoria_s"] = round(time.time() - t0, 2)

    # 2. Planejador decide SE e COMO buscar
    t = time.time()
    plano = planejar(pergunta, memorias)
    tempos["planejador_s"] = round(time.time() - t, 2)

    web, telem_meta = [], []
    if plano["rota"] != "memoria":
        # 3. Busca web via Telem (auto-roteamento), uma por consulta reescrita
        t = time.time()
        for consulta in plano["consultas_web"]:
            r = sources.buscar_web(consulta)
            telem_meta.append({"consulta": consulta, **r["metadados"]})
            web.extend(r["resultados"])
        # remove URLs repetidas entre as consultas
        vistos, unicos = set(), []
        for w in web:
            if w["url"] not in vistos:
                vistos.add(w["url"])
                unicos.append(w)
        web = unicos
        tempos["telem_s"] = round(time.time() - t, 2)

        # 4. Tavily extrai o texto limpo das melhores páginas
        t = time.time()
        top = web[:N_PAGINAS_EXTRAIR]
        try:
            extraidas = {p["url"]: p["conteudo"] for p in sources.extrair_paginas([w["url"] for w in top])}
        except Exception:
            extraidas = {}  # se a extração falhar, usamos os trechos da Telem
        for w in top:
            w["conteudo"] = extraidas.get(w["url"])
            w["extraido"] = bool(w["conteudo"])
        web = top
        tempos["tavily_s"] = round(time.time() - t, 2)

    # 5. Combinador escreve a resposta com citações
    t = time.time()
    if plano["rota"] == "web":
        memorias_usadas = []
    else:
        memorias_usadas = memorias
    final = responder(pergunta, memorias_usadas, web)
    tempos["combinador_s"] = round(time.time() - t, 2)
    tempos["total_s"] = round(time.time() - t0, 2)

    # Métricas de economia
    buscas_feitas = len(plano["consultas_web"])
    buscas_evitadas = 1 if plano["rota"] == "memoria" else 0
    economia = buscas_evitadas * CUSTO_BUSCA_EVITADA_USD
    n_buscadores = sum(len(t["buscadores"]) for t in telem_meta)
    custo_web = n_buscadores * CUSTO_POR_BUSCADOR_USD + (CUSTO_EXTRACAO_USD if web else 0)

    return {
        "pergunta": pergunta,
        "plano": plano,
        "memorias": memorias,
        "web": web,
        "telem": telem_meta,
        "resposta": final["resposta"],
        "fontes": final["fontes"],
        "tempos": tempos,
        "metricas": {"buscas_web": buscas_feitas, "buscas_evitadas": buscas_evitadas,
                     "economia_usd": round(economia, 4),
                     "custo_web_usd": round(custo_web, 4), "buscadores_consultados": n_buscadores},
    }
