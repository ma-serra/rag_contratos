# 📄 RAG Contratos - Sistema Inteligente de Análise de Contratos

![Pipeline](https://img.shields.io/badge/Pipeline-Docling%20%E2%86%92%20RAG%20%E2%86%92%20CSV-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema completo de processamento e análise de contratos de aluguel usando **Docling**, **RAG (Retrieval-Augmented Generation)**, **Claude AI** e **Busca Semântica**.

## 🌟 Destaques

- ✅ **Interface Web Moderna** - Streamlit com UI intuitiva
- ✅ **Extração Inteligente** - Docling para PDFs estruturados
- ✅ **Busca Semântica** - RAG com embeddings multilíngues
- ✅ **Análise com IA** - Claude AI para extração de dados
- ✅ **Exportação Completa** - CSV e JSON estruturados
- ✅ **Deploy Fácil** - Streamlit Cloud, Render, ou local

## 🚀 Início Rápido

### 1. Instalar

```bash
git clone https://github.com/ma-serra/rag_contratos.git
cd rag_contratos
pip install -r requirements.txt
```

### 2. Configurar

```bash
echo "ANTHROPIC_API_KEY=sua_chave_aqui" > .env
```

### 3. Executar Interface Web

```bash
streamlit run app.py
```

Abra `http://localhost:8501` no navegador e pronto! 🎉

### OU: Executar CLI

```bash
python pipeline_contratos.py
```

## 🎯 Funcionalidades

### 📤 Upload e Processamento
- Upload de múltiplos PDFs
- Processamento automático com Docling
- Extração de seções e tabelas
- Indexação vetorial com ChromaDB

### 🔍 Busca Semântica
- Perguntas em linguagem natural (português/espanhol)
- Respostas geradas por Claude AI
- Filtro por contrato específico
- Sugestões inteligentes de perguntas

### 📊 Exportação de Dados
- CSV estruturado (formato tabular)
- JSON hierárquico (estrutura completa)
- Download direto pela interface
- Preview de dados extraídos

### 📈 Análise Avançada
- Resumos automáticos de contratos
- Comparação entre múltiplos contratos
- Métricas e estatísticas
- Análise de cláusulas

## ☁️ Deploy Online (Grátis!)

### Streamlit Cloud

1. Fork este repositório
2. Acesse [streamlit.io/cloud](https://streamlit.io/cloud)
3. Configure:
   - Repository: seu fork
   - Main file: `app.py`
4. Adicione Secret: `ANTHROPIC_API_KEY`
5. Deploy! 🚀

**Resultado:** URL pública tipo `https://seu-app.streamlit.app`

Veja mais opções em [COMO_USAR.md](COMO_USAR.md)

## 📚 Documentação

- **[📘 COMO_USAR.md](COMO_USAR.md)** - Guia completo: local, deploy, troubleshooting
- **[📗 PIPELINE_USAGE.md](PIPELINE_USAGE.md)** - Documentação técnica detalhada
- **[📙 QUICK_START.md](QUICK_START.md)** - Teste rápido sem PDFs

## 🏗️ Arquitetura

```
PDF → Docling → RAG (ChromaDB) → Claude AI → CSV/JSON + Busca Semântica
```

Componentes:
- `src/docling_processor.py` - Extração de PDFs
- `src/rag_engine.py` - Sistema RAG + ChromaDB
- `src/csv_exporter.py` - Exportação estruturada
- `src/semantic_search.py` - Busca e Q&A
- `app.py` - **Interface Web Streamlit**
- `pipeline_contratos.py` - CLI interativo

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

