"""Grava memórias FICTÍCIAS no Mem0 para o usuário da demo.

Uso:  .venv/bin/python seed.py
Apaga antes as memórias desse usuário fictício (e só dele), para a demo
começar sempre igual. Nenhum dado real aqui.
"""
import sys
import time

import config
from sources import buscar_memoria, mem0

MEMORIAS = [
    "I am vegetarian.",
    "I am in Sunnyvale, California for the SearchHack hackathon until Sunday.",
    "I prefer running in the morning, around 6:30 am, about 5 km.",
    "My dinner budget is up to $30 per person.",
    "I am allergic to peanuts.",
    "I fly back to São Paulo on Monday morning from SFO.",
    "I don't have a car here; I use Caltrain and Uber.",
    "My favorite NBA team is the Golden State Warriors.",
    "My sister Ana's birthday is November 20 and she loves books about design.",
    "I am relearning Python after years without coding.",
]


def contar(uid: str) -> int:
    return len(mem0.get_all(filters={"user_id": uid}).get("results", []))


def main():
    uid = config.DEMO_USER_ID
    if not uid.startswith(("search-hack", "demo-")):
        sys.exit(f"Recusado: '{uid}' não parece um usuário fictício de demo.")

    print(f"Apagando memórias antigas de '{uid}'", end="", flush=True)
    mem0.delete_all(user_id=uid)
    # O delete do Mem0 roda em segundo plano: esperar ele terminar antes de
    # gravar, senão ele apaga também as memórias novas.
    for _ in range(24):  # até ~2 min
        if not contar(uid):
            break
        time.sleep(5)
        print(".", end="", flush=True)
    print(" ok")

    for i, texto in enumerate(MEMORIAS, 1):
        mem0.add(texto, user_id=uid)
        print(f"  {i:2d}. {texto}")

    # A gravação também roda em segundo plano: esperar todas aparecerem.
    print("Esperando o Mem0 processar", end="", flush=True)
    for _ in range(24):  # até ~2 min
        time.sleep(5)
        print(".", end="", flush=True)
        if contar(uid) >= len(MEMORIAS):
            break
    print(f"\nPronto: {contar(uid)} memórias de '{uid}' no Mem0.")
    print("Teste:", buscar_memoria("what do I eat?", uid, top_k=2))


if __name__ == "__main__":
    main()
