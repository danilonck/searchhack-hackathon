"""Carrega o .env e guarda as configurações num lugar só.

IMPORTANTE: este arquivo precisa ser importado ANTES do mem0, porque o SDK do
Mem0 lê MEM0_TELEMETRY no momento do import.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env e coloca cada linha em os.environ

PLANNER_MODEL = os.getenv("PLANNER_MODEL", "anthropic/claude-haiku-5.5")
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "anthropic/claude-haiku-5.5")
DEMO_USER_ID = os.getenv("DEMO_USER_ID", "search-hack")

# FinOps: a Telem escolhe (auto-roteamento) só entre estes buscadores.
TELEM_PROVIDERS = [p.strip() for p in os.getenv("TELEM_PROVIDERS", "exa,tavily,brave").split(",") if p.strip()]
