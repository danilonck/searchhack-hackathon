"""Tela da demo: Memory-aware search router.

Rodar:  .venv/bin/streamlit run app.py
"""
import re

import streamlit as st

import config
from pipeline import CUSTO_BUSCA_EVITADA_USD, executar

st.set_page_config(page_title="Memory-aware Search Router", page_icon="🧭", layout="wide")

ROTA_INFO = {
    "memoria": ("🧠 Memory only", "No web search needed: answered from what we know about you."),
    "web": ("🌐 Web only", "Fresh facts from the web; your memories don't change the search."),
    "ambos": ("🧠 + 🌐 Memory + Web", "Web search personalized with your memories."),
}

EXEMPLOS = [
    "What time do I usually go running, and how far?",
    "Who won the last Golden State Warriors game?",
    "Recommend a restaurant for dinner tonight",
    "What should I get my sister for her birthday?",
    "Will I need a jacket for my morning run tomorrow?",
]

# Métricas acumuladas na sessão (somam a cada pergunta).
if "historico" not in st.session_state:
    st.session_state.historico = []


# ---------------- Barra lateral: usuário e economia acumulada ----------------
with st.sidebar:
    st.header("👤 User")
    user_id = st.selectbox("Demo user (fictional)", [config.DEMO_USER_ID])
    st.caption("Memories are stored per user in Mem0.")

    st.header("💰 Savings this session")
    h = st.session_state.historico
    evitadas = sum(r["metricas"]["buscas_evitadas"] for r in h)
    feitas = sum(r["metricas"]["buscas_web"] for r in h)
    economia = sum(r["metricas"]["economia_usd"] for r in h)
    gasto = sum(r["metricas"]["custo_web_usd"] for r in h)
    c1, c2 = st.columns(2)
    c1.metric("Questions", len(h))
    c2.metric("Web searches avoided", evitadas)
    c1.metric("Web searches run", feitas)
    c2.metric("Est. saved", f"${economia:.3f}")
    st.caption(
        f"Estimate: an always-search assistant pays ~${CUSTO_BUSCA_EVITADA_USD:.3f} per question "
        f"(Telem routes to ~7 providers × $0.005 + page extraction). Spent on web so far: ${gasto:.3f}."
    )


# ---------------- Área principal ----------------
st.title("🧭 Memory-aware Search Router")
st.write("Assistants search the web for everything. This one first checks **what it knows about you**, "
         "then decides **whether** to search and **how** to search.")

st.write("**Try:**")
cols = st.columns(len(EXEMPLOS))
for col, ex in zip(cols, EXEMPLOS):
    if col.button(ex, use_container_width=True):
        st.session_state.pergunta = ex

pergunta = st.text_input("Your question", key="pergunta", placeholder="Ask anything…")
enviar = st.button("Ask", type="primary")

if (enviar or pergunta) and pergunta.strip():
    # Evita rodar de novo a mesma pergunta quando a tela recarrega.
    if st.session_state.get("ultima") != (pergunta, user_id):
        with st.spinner("Planning → searching → answering…"):
            r = executar(pergunta, user_id)
        st.session_state.ultima = (pergunta, user_id)
        st.session_state.resultado = r
        st.session_state.historico.append(r)
        st.rerun()  # atualiza a barra lateral com as métricas novas

r = st.session_state.get("resultado")
if r:
    plano = r["plano"]
    titulo, explicacao = ROTA_INFO[plano["rota"]]

    # 1. Rota e motivo
    st.subheader(f"Route: {titulo}")
    st.info(f"**Why:** {plano['motivo']}")
    if plano.get("fallback"):
        st.warning("Planner fallback: searching everything.")

    # 2. Consulta original vs. reescrita
    if plano["consultas_web"]:
        a, b = st.columns(2)
        a.markdown("**Your question**")
        a.code(r["pergunta"], language=None)
        b.markdown("**Personalized web queries** (rewritten with memory)")
        for q in plano["consultas_web"]:
            b.code(q, language=None)
    else:
        st.success("✅ 0 web searches — answered from memory.")

    # 3. Resposta com citações
    st.subheader("Answer")
    resposta = re.sub(r"\[(M\d+|W\d+)\]", r"`\1`", r["resposta"])  # destaca [M1], [W2]
    st.markdown(resposta)

    # 4. Fontes
    st.subheader("Sources cited")
    citadas = set(re.findall(r"\[(M\d+|W\d+)\]", r["resposta"]))
    for f in [f for f in r["fontes"] if f["id"] in citadas] or r["fontes"]:
        if f["tipo"] == "memoria":
            st.markdown(f"`{f['id']}` 🧠 {f['texto']}")
        else:
            st.markdown(f"`{f['id']}` 🌐 [{f['titulo'] or f['url']}]({f['url']})")

    # 5. Bastidores: Telem, Tavily e tempos
    with st.expander("⚙️ Under the hood: Telem routing, Tavily extraction, timings", expanded=True):
        m, t = r["metricas"], r["tempos"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total time", f"{t['total_s']}s")
        k2.metric("Web searches", m["buscas_web"])
        k3.metric("Providers queried", m["buscadores_consultados"])
        k4.metric("Est. web cost", f"${m['custo_web_usd']:.3f}")

        for tm in r["telem"]:
            st.markdown(f"**Telem auto-routing** for `{tm['consulta']}`  \n"
                        f"Topic: `{tm.get('topico')}` · chosen (best first): "
                        + ", ".join(f"`{p}`" for p in tm["escolhidos"])
                        + f"  \nTrace: `{tm['interaction_id']}`")
            st.dataframe(
                [{"provider": b["nome"], "status": b["status"],
                  "latency_ms": b["latencia_ms"], "results": b["n_resultados"]}
                 for b in tm["buscadores"]],
                hide_index=True, use_container_width=True,
            )
        if r["web"]:
            st.markdown("**Tavily extract** (clean page content for the answer)")
            for w in r["web"]:
                st.markdown(f"- {'✅ extracted' if w.get('extraido') else '⚠️ snippet only'} — {w['url']}")
        st.caption("Timings (s): " + ", ".join(f"{k.replace('_s', '')} {v}" for k, v in t.items()))
