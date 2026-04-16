import os, json, tempfile
import streamlit as st
import anthropic
import chromadb
import pandas as pd
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions

st.set_page_config(page_title="RAG Contratos", page_icon="📄", layout="wide")
st.title("📄 RAG Contratos — Análise Inteligente")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    api_key = st.text_input("🔑 Anthropic API Key", type="password")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
        st.success("API Key configurada ✓")
    else:
        st.warning("Configure a API Key")

# ── Estado de sessão ─────────────────────────────────────────────────────────
if "chroma" not in st.session_state:
    ef = embedding_functions.DefaultEmbeddingFunction()
    client = chromadb.EphemeralClient()
    st.session_state.chroma = client.get_or_create_collection("contratos", embedding_function=ef)
    st.session_state.contracts = []

collection = st.session_state.chroma

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📤 Upload & Processar", "🔍 Busca Semântica", "📊 Exportar CSV"])

# ── TAB 1: Upload ─────────────────────────────────────────────────────────────
with tab1:
    files = st.file_uploader("Selecione PDFs de contratos", type="pdf", accept_multiple_files=True)
    if files and st.button("🚀 Processar", type="primary"):
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        bar = st.progress(0)
        for i, f in enumerate(files):
            cid = f.name.replace(".pdf", "")
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(f.read()); tmp_path = tmp.name
            reader = PdfReader(tmp_path)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
            os.unlink(tmp_path)
            chunks = splitter.split_text(text)
            ids = [f"{cid}_c{j}" for j in range(len(chunks))]
            metas = [{"contract_id": cid, "file": f.name}] * len(chunks)
            collection.add(ids=ids, documents=chunks, metadatas=metas)
            if cid not in st.session_state.contracts:
                st.session_state.contracts.append(cid)
            bar.progress((i + 1) / len(files))
            st.success(f"✓ {f.name} — {len(chunks)} chunks indexados")

# ── TAB 2: Busca ──────────────────────────────────────────────────────────────
with tab2:
    contracts = st.session_state.contracts
    col1, col2 = st.columns([3, 1])
    query = col1.text_input("Pergunta", placeholder="Ex: Qual é a renda mensal?")
    filtro = col2.selectbox("Contrato", ["Todos"] + contracts)

    if query and not api_key:
        st.error("Configure a API Key na barra lateral.")
    elif query:
        where = {"contract_id": filtro} if filtro != "Todos" else None
        res = collection.query(query_texts=[query], n_results=4, where=where) if where else \
              collection.query(query_texts=[query], n_results=4)
        ctx = "\n\n".join(res["documents"][0])
        client_ai = anthropic.Anthropic(api_key=api_key)
        with st.spinner("Gerando resposta..."):
            msg = client_ai.messages.create(
                model="claude-3-5-sonnet-20241022", max_tokens=800,
                messages=[{"role": "user", "content":
                    f"Com base nestes trechos de contrato, responda em português:\n\n{ctx}\n\nPergunta: {query}"}])
        st.info(msg.content[0].text)
        with st.expander("Ver trechos usados"):
            for d in res["documents"][0]:
                st.text(d[:300] + "…")

    st.markdown("**Sugestões:**")
    sugs = ["Qual é a renda mensal?","Quem é o arrendador?","Duração do contrato?","Valor da fiança?","Endereço do imóvel?"]
    cols = st.columns(len(sugs))
    for c, s in zip(cols, sugs):
        c.button(s, key=s, use_container_width=True)

# ── TAB 3: CSV ────────────────────────────────────────────────────────────────
with tab3:
    if not st.session_state.contracts:
        st.warning("Nenhum contrato indexado. Faça upload primeiro.")
    elif not api_key:
        st.error("Configure a API Key.")
    else:
        if st.button("📊 Gerar CSV", type="primary"):
            rows = []
            client_ai = anthropic.Anthropic(api_key=api_key)
            prog = st.progress(0)
            for i, cid in enumerate(st.session_state.contracts):
                res = collection.query(query_texts=["informações contrato"], n_results=8, where={"contract_id": cid})
                text = "\n".join(res["documents"][0])
                msg = client_ai.messages.create(
                    model="claude-3-5-sonnet-20241022", max_tokens=1000,
                    messages=[{"role": "user", "content":
                        f'Extraia do contrato abaixo e retorne APENAS JSON com: contract_id, arrendador_nome, arrendador_documento, arrendatario_nome, arrendatario_documento, imovel_endereco, renda_mensal, fianca, duracao, data_inicio.\n\nContrato:\n{text}'}])
                try:
                    txt = msg.content[0].text
                    if "```" in txt: txt = txt.split("```")[1].lstrip("json").strip().rstrip("```")
                    data = json.loads(txt)
                    data["contract_id"] = cid
                    rows.append(data)
                except:
                    rows.append({"contract_id": cid, "erro": "parse falhou"})
                prog.progress((i + 1) / len(st.session_state.contracts))
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Baixar CSV", df.to_csv(index=False), "contratos.csv", "text/csv")
