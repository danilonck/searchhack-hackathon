"""Grava memórias FICTÍCIAS no Mem0 para os usuários da demo.

Uso:  .venv/bin/python seed.py              (todos os usuários)
      .venv/bin/python seed.py search-hack-maria   (só um)
Apaga antes as memórias de cada usuário fictício (e só dele), para a demo
começar sempre igual. Nenhum dado real aqui.
"""
import sys
import time

import config
from sources import buscar_memoria, mem0

# Duas pessoas FICTÍCIAS com perfis opostos: a mesma pergunta deve gerar
# buscas diferentes para cada uma.
PERSONAS = {
    config.DEMO_USER_ID: {
        "nome": "Alex — vegetarian runner, no car",
        "memorias": [
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
        ],
    },
    "search-hack-maria": {
        "nome": "Maria — steak lover, evening cyclist, has a car",
        "memorias": [
            "I love steak and barbecue; I eat meat almost every day.",
            "I live in Palo Alto, California.",
            "I go road cycling in the evening, around 6 pm, about 30 km.",
            "For a nice dinner I'm happy to spend up to $100 per person.",
            "I am lactose intolerant.",
            "I drive a car and prefer places with easy parking.",
            "My favorite NBA team is the Los Angeles Lakers.",
            "My brother Leo's birthday is December 3 and he loves cooking and kitchen gadgets.",
            "I fly to New York for work on Tuesday.",
            "I prefer quiet places; I don't like loud bars.",
        ],
    },
}


def contar(uid: str) -> int:
    return len(mem0.get_all(filters={"user_id": uid}).get("results", []))


def semear(uid: str, memorias: list[str]):
    if not uid.startswith(("search-hack", "demo-")):
        sys.exit(f"Recusado: '{uid}' não parece um usuário fictício de demo.")

    print(f"\n=== {uid} ===")
    print("Apagando memórias antigas", end="", flush=True)
    mem0.delete_all(user_id=uid)
    # O delete do Mem0 roda em segundo plano: esperar ele terminar antes de
    # gravar, senão ele apaga também as memórias novas.
    for _ in range(24):  # até ~2 min
        if not contar(uid):
            break
        time.sleep(5)
        print(".", end="", flush=True)
    time.sleep(10)  # folga: o contador zera um pouco antes do delete terminar
    print(" ok")

    for i, texto in enumerate(memorias, 1):
        mem0.add(texto, user_id=uid)
        print(f"  {i:2d}. {texto}")

    # A gravação também roda em segundo plano: esperar todas aparecerem.
    print("Esperando o Mem0 processar", end="", flush=True)
    for _ in range(24):  # até ~2 min
        time.sleep(5)
        print(".", end="", flush=True)
        if contar(uid) >= len(memorias):
            break
    print(f"\nPronto: {contar(uid)} de {len(memorias)} memórias no Mem0.")
    print("Teste:", buscar_memoria("what do I eat?", uid, top_k=2))


def main():
    escolhidos = sys.argv[1:] or list(PERSONAS)
    for uid in escolhidos:
        semear(uid, PERSONAS[uid]["memorias"])


if __name__ == "__main__":
    main()
