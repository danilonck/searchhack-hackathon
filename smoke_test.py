"""Testa cada serviço sozinho.

Uso:  .venv/bin/python smoke_test.py telem | tavily | mem0
"""
import sys
import time

import config
import sources


def testar_telem():
    r = sources.buscar_web("weather in Sunnyvale this weekend", num_results=3)
    print("Metadados:", r["metadados"])
    for x in r["resultados"][:5]:
        print(f"- [{x['buscador']}] {x['titulo']}\n  {x['url']}")


def testar_tavily():
    paginas = sources.extrair_paginas(["https://en.wikipedia.org/wiki/Sunnyvale,_California"])
    for p in paginas:
        print(p["url"], "->", len(p["conteudo"]), "caracteres")
        print(p["conteudo"][:300], "...")


def testar_mem0():
    uid = config.DEMO_USER_ID
    print("Gravando uma memória de teste para", uid)
    sources.mem0.add("I prefer running in the morning.", user_id=uid)
    for espera in (3, 6, 10):
        time.sleep(espera)
        achadas = sources.buscar_memoria("when do I like to exercise?", uid)
        if achadas:
            print(f"Achou depois de ~{espera}s:", achadas)
            return
        print(f"... ainda nada após {espera}s")
    print("Não achou. O Mem0 pode estar processando em segundo plano.")


if __name__ == "__main__":
    {"telem": testar_telem, "tavily": testar_tavily, "mem0": testar_mem0}[sys.argv[1]]()
