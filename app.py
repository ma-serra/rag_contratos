#!/usr/bin/env python3
"""
Interface Web para o Pipeline de Contratos
Usando Streamlit para interface amigável
"""
import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import tempfile
import pandas as pd
import json

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.docling_processor import DoclingProcessor
from src.rag_engine import RAGEngine
from src.csv_exporter import CSVExporter
from src.semantic_search import SemanticSearch

# Configuração da página
st.set_page_config(
    page_title="RAG Contratos - Análise Inteligente",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar sessão
if 'pipeline_initialized' not in st.session_state:
    st.session_state.pipeline_initialized = False
    st.session_state.rag = None
    st.session_state.search = None
    st.session_state.processed_contracts = []

def initialize_pipeline():
    """Inicializa o pipeline"""
    try:
        with st.spinner("Inicializando sistema..."):
            os.makedirs("contratos", exist_ok=True)
            os.makedirs("output", exist_ok=True)

            st.session_state.docling = DoclingProcessor()
            st.session_state.rag = RAGEngine(persist_directory="chromadb_storage")
            st.session_state.exporter = CSVExporter()
            st.session_state.search = SemanticSearch(st.session_state.rag)
            st.session_state.pipeline_initialized = True

        return True
    except Exception as e:
        st.error(f"Erro ao inicializar: {e}")
        return False

def main():
    """Função principal da aplicação"""

    # Header
    st.markdown('<div class="main-header">📄 RAG Contratos - Análise Inteligente</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Docling → RAG → CSV → Busca Semântica</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=RAG+Contratos", use_container_width=True)

        st.markdown("### ⚙️ Configuração")

        # Verificar API Key
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Sua chave da API Anthropic"
        )

        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
            st.success("✓ API Key configurada")
        else:
            st.warning("⚠️ Configure sua API Key")

        st.markdown("---")

        # Inicializar pipeline
        if st.button("🚀 Inicializar Sistema", use_container_width=True):
            if initialize_pipeline():
                st.success("✓ Sistema inicializado!")
                st.rerun()

        if st.session_state.pipeline_initialized:
            st.success("✓ Sistema pronto")

            # Contratos indexados
            contracts = st.session_state.rag.get_all_contracts()
            st.markdown(f"**Contratos indexados:** {len(contracts)}")

            if contracts:
                with st.expander("Ver contratos"):
                    for contract in contracts:
                        st.text(f"• {contract}")

        st.markdown("---")
        st.markdown("### 📚 Sobre")
        st.markdown("""
        Sistema de análise de contratos usando:
        - **Docling** para extração
        - **RAG** para indexação
        - **Claude AI** para análise
        - **Busca Semântica** em português
        """)

    # Verificar se sistema está inicializado
    if not st.session_state.pipeline_initialized:
        st.markdown('<div class="info-box">👈 Configure a API Key e clique em "Inicializar Sistema" na barra lateral</div>', unsafe_allow_html=True)

        # Instruções
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🚀 Como Começar")
            st.markdown("""
            1. **Configure a API Key** na barra lateral
            2. **Clique em "Inicializar Sistema"**
            3. **Faça upload de um PDF** de contrato
            4. **Faça perguntas** sobre o contrato
            """)

        with col2:
            st.markdown("### 📋 Funcionalidades")
            st.markdown("""
            - ✅ Upload e processamento de PDFs
            - ✅ Extração automática de dados
            - ✅ Busca semântica em linguagem natural
            - ✅ Exportação para CSV/JSON
            - ✅ Comparação de contratos
            """)

        return

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Processar",
        "🔍 Busca Semântica",
        "📊 Exportar Dados",
        "📈 Análise"
    ])

    # TAB 1: Upload e Processamento
    with tab1:
        st.markdown("### 📤 Upload de Contratos")

        uploaded_files = st.file_uploader(
            "Selecione um ou mais PDFs de contratos",
            type=['pdf'],
            accept_multiple_files=True,
            help="Faça upload dos contratos em PDF para processar"
        )

        if uploaded_files:
            col1, col2 = st.columns([3, 1])

            with col2:
                process_button = st.button("🚀 Processar Contratos", use_container_width=True)

            if process_button:
                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []

                for i, uploaded_file in enumerate(uploaded_files):
                    # Atualizar progresso
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.text(f"Processando {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")

                    # Salvar arquivo temporário
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    try:
                        # Processar
                        contract_id = Path(uploaded_file.name).stem

                        # 1. Docling
                        doc_data = st.session_state.docling.process_pdf(tmp_path)

                        # 2. RAG
                        st.session_state.rag.index_document(
                            doc_data=doc_data,
                            contract_id=contract_id
                        )

                        if doc_data.get("sections"):
                            st.session_state.rag.index_sections(
                                sections=doc_data["sections"],
                                contract_id=contract_id
                            )

                        # 3. Extrair dados
                        structured_data = st.session_state.exporter.extract_structured_data(
                            contract_text=doc_data["full_text"],
                            contract_id=contract_id
                        )

                        results.append({
                            "contract_id": contract_id,
                            "file_name": uploaded_file.name,
                            "structured_data": structured_data,
                            "num_sections": len(doc_data.get("sections", [])),
                            "text_length": len(doc_data.get("full_text", ""))
                        })

                    except Exception as e:
                        st.error(f"Erro ao processar {uploaded_file.name}: {e}")

                    finally:
                        # Limpar arquivo temporário
                        os.unlink(tmp_path)

                progress_bar.progress(1.0)
                status_text.text("✓ Processamento concluído!")

                # Mostrar resultados
                st.markdown('<div class="success-box">✅ Contratos processados com sucesso!</div>', unsafe_allow_html=True)

                for result in results:
                    with st.expander(f"📄 {result['file_name']}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Seções", result['num_sections'])
                        col2.metric("Caracteres", result['text_length'])
                        col3.metric("Status", "✓ Indexado")

                        # Mostrar dados extraídos
                        st.json(result['structured_data'])

    # TAB 2: Busca Semântica
    with tab2:
        st.markdown("### 🔍 Busca Semântica")

        contracts = st.session_state.rag.get_all_contracts()

        if not contracts:
            st.markdown('<div class="warning-box">⚠️ Nenhum contrato indexado. Faça upload na aba "Upload & Processar"</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([2, 1])

            with col1:
                query = st.text_input(
                    "Faça sua pergunta",
                    placeholder="Ex: Qual é o valor da renda mensal?",
                    help="Digite sua pergunta em linguagem natural"
                )

            with col2:
                contract_filter = st.selectbox(
                    "Buscar em",
                    ["Todos os contratos"] + contracts,
                    help="Filtrar por contrato específico"
                )

            if query:
                with st.spinner("Buscando..."):
                    contract_id = None if contract_filter == "Todos os contratos" else contract_filter

                    # Buscar
                    result = st.session_state.search.search(
                        query=query,
                        contract_id=contract_id,
                        n_results=3,
                        use_llm=True
                    )

                    # Mostrar resposta
                    st.markdown("#### 💡 Resposta")
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(result.get("llm_response", "Não foi possível gerar resposta"))
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Mostrar trechos relevantes
                    with st.expander("📑 Ver trechos relevantes"):
                        for i, (doc, metadata) in enumerate(zip(
                            result["search_results"]["documents"],
                            result["search_results"]["metadatas"]
                        )):
                            st.markdown(f"**Trecho {i+1}** (Contrato: {metadata.get('contract_id', 'N/A')})")
                            st.text(doc[:500] + "..." if len(doc) > 500 else doc)
                            st.markdown("---")

            # Perguntas sugeridas
            st.markdown("#### 💭 Perguntas Sugeridas")
            col1, col2, col3 = st.columns(3)

            suggestions = [
                "Qual é o valor da renda mensal?",
                "Quem é o arrendador?",
                "Qual é a duração do contrato?",
                "Qual é o endereço do imóvel?",
                "Quem são os arrendatários?",
                "Quanto é a fiança?"
            ]

            for i, suggestion in enumerate(suggestions):
                col = [col1, col2, col3][i % 3]
                with col:
                    if st.button(suggestion, use_container_width=True):
                        st.rerun()

    # TAB 3: Exportar
    with tab3:
        st.markdown("### 📊 Exportar Dados")

        contracts = st.session_state.rag.get_all_contracts()

        if not contracts:
            st.markdown('<div class="warning-box">⚠️ Nenhum contrato indexado</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**{len(contracts)} contratos** prontos para exportar")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Exportar CSV", use_container_width=True):
                    with st.spinner("Exportando..."):
                        # Coletar dados
                        contracts_data = []

                        for contract_id in contracts:
                            results = st.session_state.rag.search_by_contract(
                                query="informações do contrato",
                                contract_id=contract_id,
                                n_results=10
                            )

                            full_text = "\n".join(results["documents"])
                            structured = st.session_state.exporter.extract_structured_data(
                                contract_text=full_text,
                                contract_id=contract_id
                            )

                            contracts_data.append(structured)

                        # Exportar
                        df = st.session_state.exporter.export_to_csv(
                            contracts_data,
                            "output/contratos_exportados.csv"
                        )

                        st.success("✓ CSV exportado!")

                        # Download
                        csv = df.to_csv(index=False, encoding='utf-8')
                        st.download_button(
                            label="📥 Baixar CSV",
                            data=csv,
                            file_name="contratos.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

            with col2:
                if st.button("📥 Exportar JSON", use_container_width=True):
                    with st.spinner("Exportando..."):
                        contracts_data = []

                        for contract_id in contracts:
                            results = st.session_state.rag.search_by_contract(
                                query="informações do contrato",
                                contract_id=contract_id,
                                n_results=10
                            )

                            full_text = "\n".join(results["documents"])
                            structured = st.session_state.exporter.extract_structured_data(
                                contract_text=full_text,
                                contract_id=contract_id
                            )

                            contracts_data.append(structured)

                        st.session_state.exporter.export_to_json(
                            contracts_data,
                            "output/contratos_exportados.json"
                        )

                        st.success("✓ JSON exportado!")

                        # Download
                        json_str = json.dumps(contracts_data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📥 Baixar JSON",
                            data=json_str,
                            file_name="contratos.json",
                            mime="application/json",
                            use_container_width=True
                        )

            # Preview dos dados
            if st.checkbox("👁️ Visualizar preview dos dados"):
                with st.spinner("Carregando dados..."):
                    sample_contract = contracts[0]
                    results = st.session_state.rag.search_by_contract(
                        query="informações do contrato",
                        contract_id=sample_contract,
                        n_results=10
                    )

                    full_text = "\n".join(results["documents"])
                    structured = st.session_state.exporter.extract_structured_data(
                        contract_text=full_text,
                        contract_id=sample_contract
                    )

                    st.json(structured)

    # TAB 4: Análise
    with tab4:
        st.markdown("### 📈 Análise de Contratos")

        contracts = st.session_state.rag.get_all_contracts()

        if not contracts:
            st.markdown('<div class="warning-box">⚠️ Nenhum contrato indexado</div>', unsafe_allow_html=True)
        else:
            # Resumo de contrato
            st.markdown("#### 📋 Resumo de Contrato")

            selected_contract = st.selectbox(
                "Selecione um contrato",
                contracts,
                key="summary_contract"
            )

            if st.button("📝 Gerar Resumo"):
                with st.spinner("Gerando resumo..."):
                    summary = st.session_state.search.get_contract_summary(selected_contract)
                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                    st.markdown(summary)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            # Comparação de contratos
            if len(contracts) > 1:
                st.markdown("#### ⚖️ Comparar Contratos")

                col1, col2 = st.columns(2)

                with col1:
                    contracts_to_compare = st.multiselect(
                        "Selecione contratos para comparar",
                        contracts,
                        max_selections=3
                    )

                with col2:
                    aspect = st.selectbox(
                        "Aspecto a comparar",
                        [
                            "condições econômicas",
                            "duração e prazos",
                            "partes envolvidas",
                            "características do imóvel"
                        ]
                    )

                if len(contracts_to_compare) >= 2 and st.button("⚖️ Comparar"):
                    with st.spinner("Comparando contratos..."):
                        comparison = st.session_state.search.compare_contracts(
                            contract_ids=contracts_to_compare,
                            aspect=aspect
                        )
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown(comparison)
                        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
