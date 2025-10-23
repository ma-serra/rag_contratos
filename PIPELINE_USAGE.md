# Pipeline de Processamento de Contratos

## Visão Geral

Este pipeline integrado processa contratos de aluguel em PDF através de 4 etapas principais:

1. **Docling** - Extração de conteúdo estruturado de PDFs
2. **RAG** - Indexação em banco vetorial com embeddings semânticos
3. **CSV** - Exportação de dados estruturados
4. **Busca Semântica** - Interface de consulta em linguagem natural

## Arquitetura

```
contratos/           # PDFs de entrada
    ├── contrato_001.pdf
    └── contrato_002.pdf
         ↓
    [Docling Processor]
         ↓
    [RAG Engine]
         ↓
    [CSV Exporter] → output/contratos_exportados.csv
         ↓
    [Semantic Search] → Busca interativa
```

## Componentes

### 1. DoclingProcessor (`src/docling_processor.py`)

Processa PDFs e extrai:
- Texto completo
- Markdown estruturado
- Seções do documento
- Tabelas

**Uso básico:**
```python
from src.docling_processor import DoclingProcessor

processor = DoclingProcessor()
doc_data = processor.process_pdf("caminho/para/contrato.pdf")
```

### 2. RAGEngine (`src/rag_engine.py`)

Sistema de recuperação com:
- ChromaDB para armazenamento vetorial
- Embeddings multilíngues (português)
- Chunking inteligente de texto
- Busca semântica

**Uso básico:**
```python
from src.rag_engine import RAGEngine

rag = RAGEngine()
rag.index_document(doc_data, contract_id="C001")

# Buscar
results = rag.search("Qual é o valor da renda?")
```

### 3. CSVExporter (`src/csv_exporter.py`)

Exporta dados estruturados:
- Extração com Claude AI
- Formato tabular (CSV)
- Formato hierárquico (JSON)

**Estrutura de dados:**
```
- Arrendador (nome, documento, endereço)
- Arrendatários (múltiplos)
- Imóvel (endereço, superfície, ref. catastral)
- Condições econômicas (renda, gastos, IBI, fiança)
- Duração (prazo, datas)
```

### 4. SemanticSearch (`src/semantic_search.py`)

Interface de busca com:
- Busca semântica no ChromaDB
- Geração de respostas com Claude
- Resumos automáticos
- Comparação entre contratos

**Uso básico:**
```python
from src.semantic_search import SemanticSearch

search = SemanticSearch(rag)
answer = search.ask_question("Quem é o arrendador?", contract_id="C001")
```

## Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env`:

```bash
ANTHROPIC_API_KEY=sua_chave_aqui
```

### 3. Preparar diretórios

```bash
mkdir -p contratos output
```

Coloque seus PDFs de contratos na pasta `contratos/`.

## Uso do Pipeline Completo

### Modo Interativo (Recomendado)

```bash
python pipeline_contratos.py
```

Menu de opções:
1. **Processar todos os contratos** - Executa Docling + RAG em todos os PDFs
2. **Processar contrato específico** - Processa um PDF individual
3. **Exportar para CSV** - Gera CSV e JSON com dados estruturados
4. **Busca semântica** - Modo interativo de perguntas e respostas
5. **Demo de busca** - Demonstração automática
6. **Listar contratos** - Mostra contratos indexados
7. **Gerar resumo** - Resumo automático de um contrato

### Uso Programático

```python
from pipeline_contratos import ContractPipeline

# Inicializar pipeline
pipeline = ContractPipeline(
    contracts_dir="contratos",
    output_dir="output",
    db_dir="chromadb_storage"
)

# Processar todos os contratos
results = pipeline.process_all_contracts()

# Exportar para CSV
pipeline.export_to_csv(results)

# Busca semântica
answer = pipeline.search.ask_question(
    "Qual é o valor da renda mensal?",
    contract_id="contrato_001"
)
print(answer)
```

## Exemplos de Uso

### Exemplo 1: Processar e Exportar

```python
# Processar contratos
pipeline = ContractPipeline()
results = pipeline.process_all_contracts()

# Exportar para CSV
pipeline.export_to_csv(results)
```

### Exemplo 2: Busca Semântica

```python
# Buscar em contrato específico
answer = pipeline.search.ask_question(
    "Qual é a duração do contrato?",
    contract_id="contrato_001"
)

# Buscar em todos os contratos
results = pipeline.search.search(
    "contratos com renda superior a 1000 euros"
)
```

### Exemplo 3: Resumo de Contrato

```python
summary = pipeline.search.get_contract_summary("contrato_001")
print(summary)
```

### Exemplo 4: Comparar Contratos

```python
comparison = pipeline.search.compare_contracts(
    contract_ids=["contrato_001", "contrato_002"],
    aspect="condições econômicas"
)
print(comparison)
```

## Estrutura de Saída

### CSV (`output/contratos_exportados.csv`)

Colunas:
- `contract_id`
- `arrendador_nome`, `arrendador_documento`, `arrendador_endereco`
- `arrendatario_1_nome`, `arrendatario_1_documento`, ...
- `arrendatario_2_nome`, `arrendatario_2_documento`, ...
- `imovel_endereco`, `imovel_superficie`, `imovel_ref_catastral`
- `renda_mensal`, `gastos_comuns_mensal`, `ibi_mensal`, `fianca`
- `prazo`, `data_inicio`, `data_fim`

### JSON (`output/contratos_exportados.json`)

Estrutura hierárquica completa com todos os dados.

## Fluxo de Trabalho Típico

1. **Preparação**
   - Colocar PDFs em `contratos/`
   - Configurar `.env` com API key

2. **Processamento**
   ```bash
   python pipeline_contratos.py
   # Opção 1: Processar todos os contratos
   ```

3. **Exportação**
   ```bash
   # Opção 3: Exportar para CSV
   ```

4. **Análise**
   ```bash
   # Opção 4: Busca semântica interativa
   ```

## Perguntas Frequentes

**Q: Quanto tempo leva para processar um contrato?**
A: Tipicamente 30-60 segundos por contrato, dependendo do tamanho.

**Q: Posso processar contratos em outros idiomas?**
A: Sim, mas o modelo de embeddings atual é otimizado para português/espanhol.

**Q: Como melhorar a qualidade das respostas?**
A: Use perguntas específicas e diretas. O sistema funciona melhor com perguntas factuais.

**Q: Os dados são persistidos?**
A: Sim, o ChromaDB persiste automaticamente em `chromadb_storage/`.

**Q: Preciso reprocessar contratos já indexados?**
A: Não, a menos que o contrato tenha sido atualizado.

## Troubleshooting

### Erro: "API Key não configurada"
Solução: Configure `ANTHROPIC_API_KEY` no arquivo `.env`

### Erro ao processar PDF
Solução: Verifique se o PDF não está corrompido ou protegido por senha

### Resultados de busca ruins
Solução:
- Use perguntas mais específicas
- Verifique se o contrato foi indexado corretamente
- Aumente `n_results` na busca

## Performance

- **Embeddings**: Modelo multilíngue leve (~120MB)
- **Banco de dados**: ChromaDB com persistência em disco
- **Processamento**: Paralelo quando possível
- **Memória**: ~500MB para coleção de 100 contratos

## Roadmap

- [ ] Suporte para múltiplos idiomas
- [ ] Interface web
- [ ] API REST
- [ ] Validação de dados extraídos
- [ ] Detecção de cláusulas problemáticas
- [ ] Comparação automática de contratos

## Contribuindo

Melhorias são bem-vindas! Áreas de interesse:
- Novos modelos de embeddings
- Melhoria na extração de dados
- Interface de usuário
- Testes automatizados
