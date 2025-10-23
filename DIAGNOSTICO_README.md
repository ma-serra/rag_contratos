# 🏢 Sistema de Diagnóstico Jurídico Condominial - RAG

## 🎯 O Que É?

Sistema completo de diagnóstico jurídico de condomínios usando **RAG (Retrieval Augmented Generation)** + **ChromaDB** + **Claude AI**.

Analisa automaticamente múltiplos documentos:
- 📜 Convenções de condomínio
- 📋 Regimentos internos
- 📝 Atas de assembleia
- 📄 Contratos diversos

**Executando as 5 Fases do Diagnóstico Jurídico:**
1. Identificação e Extração Jurídica
2. Mapeamento Hierárquico e Classificação Normativa
3. Matriz de Conformidade Legal
4. Consolidação e Otimização
5. Documento Técnico Final

---

## 🚀 Início Rápido

### 1. Configuração

```bash
# Instalar dependências
pip install chromadb anthropic python-dotenv pandas

# Configurar API Key do Claude
echo "ANTHROPIC_API_KEY=sk-ant-api03-sua_chave_aqui" > .env
```

### 2. Exemplo Completo

```bash
# Executar exemplo com dados de demonstração
python exemplo_diagnostico.py

# Executar apenas busca RAG simples
python exemplo_diagnostico.py simples
```

###  3. Resultado

O sistema gera:
- ✅ `diagnostico_resultado.json` - Relatório completo estruturado
- ✅ Análise jurídica em 3 fases
- ✅ Identificação de problemas e recomendações

---

## 📚 Arquitetura do Sistema

```
diagnostico/
├── __init__.py
├── chunking.py          # Sistema de divisão inteligente de documentos
├── database.py          # Gerenciamento ChromaDB (armazenamento vetorial)
└── extractor.py         # Extração com Claude AI (análise jurídica)

chromadb_data/           # Banco de dados vetorial (gerado automaticamente)

exemplo_diagnostico.py   # Script de demonstração completo
```

### Fluxo de Funcionamento

```
1. DOCUMENTOS → chunking.py
   ↓ (Divide em chunks inteligentes)

2. CHUNKS → database.py
   ↓ (Vetoriza e armazena no ChromaDB)

3. QUERY → database.py (RAG)
   ↓ (Busca semântica nos chunks)

4. CHUNKS RELEVANTES → extractor.py
   ↓ (Análise com Claude AI)

5. RESULTADO ESTRUTURADO JSON
```

---

## 💡 Como Usar no Seu Código

### Exemplo 1: Adicionar Documentos

```python
from diagnostico.chunking import chunk_convencao, chunk_norma, chunk_ata
from diagnostico.database import CondominioDatabase

# Inicializar banco
db = CondominioDatabase()

# Carregar convenção do condomínio
convencao_text = """
CONVENÇÃO DO CONDOMÍNIO XYZ

Art. 1º - O condomínio é constituído...
...
"""

# Processar em chunks
chunks = chunk_convencao(
    convencao_text,
    metadata={"data_registro": "2024-01-15"}
)

# Inserir no banco
db.add_chunks(
    chunks=chunks,
    condominio_id="COND_XYZ",
    document_name="convencao_2024"
)

print(f"✓ {len(chunks)} chunks inseridos!")
```

### Exemplo 2: Busca Semântica (RAG)

```python
# Buscar informações relevantes
resultados = db.search(
    query="Quais são as penalidades previstas?",
    condominio_id="COND_XYZ",
    doc_types=["convencoes", "normas"],
    n_results=5
)

for resultado in resultados:
    print(f"Documento: {resultado['metadata']['document_name']}")
    print(f"Conteúdo: {resultado['content'][:200]}...\n")
```

### Exemplo 3: Diagnóstico Completo

```python
from diagnostico.extractor import CondominioExtractor

# Inicializar extrator
extractor = CondominioExtractor(db)

# Executar diagnóstico completo
resultado = extractor.diagnostico_completo(
    condominio_id="COND_XYZ",
    objetivo="REVISAO_CONFORMIDADE"
)

# Acessar resultados
fase1 = resultado["fases"]["fase1_identificacao"]
print(f"Denominação: {fase1['identificacao_registral']['denominacao']}")
print(f"CNPJ: {fase1['identificacao_registral']['cnpj']}")

fase3 = resultado["fases"]["fase3_conformidade"]
print(f"Problemas críticos: {len(fase3['problemas_criticos'])}")
```

---

## 🔧 Funcionalidades Detalhadas

### 1. Sistema de Chunking (`chunking.py`)

**Classes:**
- `DocumentChunker` - Chunker genérico configurável
- `DocumentChunk` - Dataclass representando um chunk

**Funções Helper:**
```python
# Chunkar por tipo de documento
chunks = chunk_contrato(text, metadata)    # Contratos
chunks = chunk_norma(text, metadata)       # Normas/Regimentos
chunks = chunk_ata(text, metadata)         # Atas
chunks = chunk_convencao(text, metadata)   # Convenções
```

**Características:**
- ✅ Divisão inteligente por estrutura jurídica (artigos, capítulos)
- ✅ Sobreposição (overlap) para manter contexto
- ✅ Preservação de metadados
- ✅ Tamanhos configuráveis

### 2. Banco de Dados Vetorial (`database.py`)

**Classe `CondominioDatabase`:**

```python
db = CondominioDatabase(persist_directory="./chromadb_data")

# Adicionar chunks
db.add_chunks(chunks, condominio_id, document_name)

# Buscar semântico (RAG)
results = db.search(query, condominio_id, doc_types, n_results)

# Listar documentos
docs = db.list_documents(condominio_id)

# Obter chunks de um documento específico
chunks = db.get_document_chunks(condominio_id, document_name, doc_type)

# Deletar documento
db.delete_document(condominio_id, document_name, doc_type)

# Estatísticas
stats = db.get_statistics()  # {'contratos': 50, 'normas': 30, ...}
```

**Coleções ChromaDB:**
- `contratos` - Contratos de todos os tipos
- `normas` - Regimentos internos e normas
- `atas` - Atas de assembleias
- `convencoes` - Convenções de condomínio

### 3. Extração Jurídica (`extractor.py`)

**Classe `CondominioExtractor`:**

```python
extractor = CondominioExtractor(db)

# FASE 1: Identificação e Extração Jurídica
fase1 = extractor.extract_fase1_identificacao(condominio_id)
# Retorna: denominação, CNPJ, estrutura física, governança

# FASE 2: Mapeamento Hierárquico
fase2 = extractor.extract_fase2_mapeamento(condominio_id)
# Retorna: disposições (constitutivas, administrativas, etc), problemas

# FASE 3: Matriz de Conformidade Legal
fase3 = extractor.extract_fase3_conformidade(condominio_id)
# Retorna: análise de conformidade, problemas críticos, recomendações

# DIAGNÓSTICO COMPLETO (todas as fases)
resultado_completo = extractor.diagnostico_completo(
    condominio_id,
    objetivo="REVISAO_CONFORMIDADE"  # ou REGIMENTO_INTERNO, ANALISE_PENALIDADES, OTIMIZACAO_GERAL
)
```

---

## 📋 Objetivos de Diagnóstico

### `REGIMENTO_INTERNO`
- **Fases**: 1, 2, 5
- **Foco**: Criar/atualizar regimento interno
- **Saída**: Estrutura para regimento + disposições regulamentáveis

### `ANALISE_PENALIDADES`
- **Fases**: 1, 2, 3
- **Foco**: Adequar sistema sancionador
- **Saída**: Penalidades conformes + procedimentos

### `REVISAO_CONFORMIDADE`
- **Fases**: 1, 2, 3, 5
- **Foco**: Auditoria legal completa
- **Saída**: Relatório técnico + plano de adequação

### `OTIMIZACAO_GERAL`
- **Fases**: Todas (1, 2, 3, 4, 5)
- **Foco**: Modernização integral
- **Saída**: Convenção consolidada + implementação

---

## 📊 Formato de Saída

### Exemplo de `diagnostico_resultado.json`:

```json
{
  "condominio_id": "COND_001",
  "objetivo": "REVISAO_CONFORMIDADE",
  "fases": {
    "fase1_identificacao": {
      "identificacao_registral": {
        "denominacao": "Condomínio Residencial Exemplo",
        "cnpj": "12.345.678/0001-90",
        "endereco": "Rua das Flores, 123, São Paulo/SP",
        "matricula": "54.321",
        "data_instituicao": "2020-01-15"
      },
      "estrutura_fisica": {
        "tipologia": "residencial",
        "unidades_autonomas": 80,
        "fracoes_ideais": "proporcional à área privativa",
        "areas_comuns": ["piscina", "salão de festas", "quadra"],
        "vagas_garagem": "vinculadas às unidades"
      },
      "governanca": {
        "estrutura_administrativa": ["síndico", "conselho fiscal"],
        "mandatos": "2 anos",
        "quoruns": {"primeira_convocacao": "2/3 dos condôminos"}
      }
    },
    "fase2_mapeamento": {
      "disposicoes_constitutivas": [...],
      "disposicoes_administrativas": [...],
      "problemas_identificados": {
        "conflitos_normativos": [],
        "lacunas": ["falta regulamentação uso piscina"],
        "vicios_quorum": []
      }
    },
    "fase3_conformidade": {
      "conformidade": [
        {
          "aspecto": "Penalidades",
          "status": "CONFORME",
          "dispositivo_legal": "CC art. 1.337",
          "consequencia": "Válida e exigível",
          "acao_recomendada": "MANTER"
        }
      ],
      "problemas_criticos": [],
      "recomendacoes_prioritarias": [
        "Regulamentar uso das áreas comuns",
        "Atualizar valores de multa"
      ]
    }
  }
}
```

---

## ⚙️ Configurações Avançadas

### Customizar Tamanho dos Chunks

```python
from diagnostico.chunking import DocumentChunker

chunker = DocumentChunker(
    chunk_size=2000,        # Tamanho máximo em caracteres
    chunk_overlap=300,      # Sobreposição entre chunks
    separators=["\n\n##", "\n\n", "\n"]  # Hierarquia de divisão
)

chunks = chunker.chunk_document(text, doc_type="convencao")
```

### Usar Diferentes Modelos Claude

```python
# Em extractor.py, linha ~100
response = self.anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",  # Alterar modelo aqui
    max_tokens=2000,
    messages=[...]
)
```

Modelos disponíveis:
- `claude-3-5-sonnet-20241022` (recomendado - mais recente)
- `claude-3-opus-20240229` (mais poderoso)
- `claude-3-sonnet-20240229` (balanceado)
- `claude-3-haiku-20240307` (mais rápido/barato)

---

## 🔍 Casos de Uso Práticos

### 1. Carregar Múltiplos Documentos de um Condomínio

```python
from diagnostico import *

db = CondominioDatabase()

# Lista de documentos
documentos = [
    ("convencao_2020.txt", "convencao"),
    ("regimento_interno.txt", "norma"),
    ("ata_2024_03.txt", "ata"),
    ("contrato_limpeza.txt", "contrato")
]

# Processar todos
for arquivo, tipo in documentos:
    with open(arquivo, 'r', encoding='utf-8') as f:
        text = f.read()

    # Chunkar conforme tipo
    if tipo == "convencao":
        chunks = chunk_convencao(text)
    elif tipo == "norma":
        chunks = chunk_norma(text)
    elif tipo == "ata":
        chunks = chunk_ata(text)
    else:
        chunks = chunk_contrato(text)

    # Inserir
    db.add_chunks(chunks, "COND_XYZ", arquivo)
    print(f"✓ {arquivo}: {len(chunks)} chunks")
```

### 2. Comparar Múltiplos Condomínios

```python
# Adicionar documentos de vários condomínios
db.add_chunks(chunks_a, "COND_A", "convencao")
db.add_chunks(chunks_b, "COND_B", "convencao")

# Buscar uma cláusula específica em ambos
query = "prazo de convocação de assembleia"

results_a = db.search(query, condominio_id="COND_A", n_results=3)
results_b = db.search(query, condominio_id="COND_B", n_results=3)

print("Condomínio A:", results_a[0]['content'])
print("Condomínio B:", results_b[0]['content'])
```

### 3. Gerar Relatório Personalizado

```python
extractor = CondominioExtractor(db)

# Executar fase específica
conformidade = extractor.extract_fase3_conformidade("COND_XYZ")

# Gerar relatório HTML
html = f"""
<html>
<head><title>Relatório de Conformidade</title></head>
<body>
<h1>Relatório de Conformidade Legal</h1>
<h2>Problemas Críticos</h2>
<ul>
"""

for problema in conformidade.get('problemas_criticos', []):
    html += f"<li>{problema}</li>"

html += """
</ul>
</body>
</html>
"""

with open("relatorio.html", "w") as f:
    f.write(html)
```

---

## 🛠️ Solução de Problemas

### Erro: "ChromaDB SHA256 hash mismatch"
```bash
# Limpar cache do ChromaDB
rm -rf ~/.cache/chroma/

# Reinstalar ChromaDB
pip uninstall chromadb
pip install chromadb
```

### Erro: "Authentication error" (API Key inválida)
```bash
# Verificar se .env existe e contém a chave
cat .env

# Deve conter:
ANTHROPIC_API_KEY=sk-ant-api03-...

# Obter nova chave em: https://console.anthropic.com
```

### Erro: "ModuleNotFoundError: No module named 'diagnostico'"
```bash
# Executar do diretório raiz do projeto
cd /home/user/rag_contratos
python exemplo_diagnostico.py
```

### Banco de Dados Vazio (0 chunks)
```python
# Verificar se chunks foram gerados
chunks = chunk_convencao(text)
print(f"Chunks gerados: {len(chunks)}")

# Verificar se add_chunks foi chamado
db.add_chunks(chunks, "COND_ID", "doc_name")

# Verificar estatísticas
print(db.get_statistics())
```

---

## 📈 Próximas Melhorias

- [ ] Suporte a PDF (PyPDF2/pdfplumber)
- [ ] Interface web (Streamlit/FastAPI)
- [ ] Exportação para Word/PDF
- [ ] Cache de resultados Claude
- [ ] Batch processing de múltiplos condomínios
- [ ] Comparação entre versões de documentos
- [ ] Alertas automáticos de não conformidade
- [ ] Integração com sistemas de gestão condominial

---

## 📄 Licença

MIT License - Livre para uso comercial e pessoal

---

## 🤝 Contribuindo

Sugestões, melhorias e PRs são bem-vindos!

1. Fork o projeto
2. Crie sua feature branch
3. Commit suas mudanças
4. Push para o branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando RAG, ChromaDB e Claude AI**
