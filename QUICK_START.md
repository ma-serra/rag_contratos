# Guia Rápido de Início

## Instalação Rápida

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar API Key
echo "ANTHROPIC_API_KEY=sua_chave_aqui" > .env

# 3. Criar diretórios
mkdir -p contratos output
```

## Teste Rápido (Sem PDF)

Se você ainda não tem PDFs de contratos, pode testar com dados de exemplo:

```python
from src.rag_engine import RAGEngine
from src.semantic_search import SemanticSearch

# Criar RAG
rag = RAGEngine()

# Adicionar dados de exemplo
rag.index_document(
    doc_data={
        "file_name": "contrato_exemplo.pdf",
        "full_text": """
        CONTRATO DE ARRENDAMIENTO

        REUNIDOS
        De una parte, INMOBILIARIA XYZ S.A., con CIF A12345678

        De otra parte, Juan Pérez García, con DNI 12345678A

        CONDICIONES ECONÓMICAS
        Renta mensual: 800 euros
        Gastos de comunidad: 50 euros mensuales
        Fianza: Una mensualidad (800 euros)

        DURACIÓN
        El contrato tendrá una duración de 5 años,
        comenzando el 01/01/2024

        INMUEBLE
        Calle Principal, 123, 3º A, Madrid
        Superficie: 75 m2
        """,
        "sections": [],
        "tables": [],
        "markdown": "",
        "metadata": {"num_pages": 1}
    },
    contract_id="ejemplo_001"
)

# Buscar
search = SemanticSearch(rag)
print(search.ask_question("Qual é a renda mensal?"))
```

## Uso com PDFs

```bash
# 1. Colocar PDFs na pasta contratos/
cp seus_contratos/*.pdf contratos/

# 2. Executar pipeline
python pipeline_contratos.py

# 3. No menu, escolher:
#    Opção 1: Processar todos os contratos
#    Opção 3: Exportar para CSV
#    Opção 4: Busca interativa
```

## Uso Direto dos Módulos

### Processar um PDF

```python
from src.docling_processor import DoclingProcessor

processor = DoclingProcessor()
doc_data = processor.process_pdf("contratos/contrato_001.pdf")

print(f"Texto extraído: {len(doc_data['full_text'])} caracteres")
print(f"Seções: {len(doc_data['sections'])}")
```

### Indexar e Buscar

```python
from src.rag_engine import RAGEngine

rag = RAGEngine()
rag.index_document(doc_data, contract_id="C001")

results = rag.search("valor da renda")
print(results["documents"])
```

### Exportar para CSV

```python
from src.csv_exporter import CSVExporter

exporter = CSVExporter()
structured = exporter.extract_structured_data(
    contract_text=doc_data["full_text"],
    contract_id="C001"
)

exporter.export_to_csv([structured], "contratos.csv")
```

## Exemplos de Perguntas

- "Qual é o valor da renda mensal?"
- "Quem é o arrendador?"
- "Quem são os arrendatários?"
- "Qual é a duração do contrato?"
- "Qual é o endereço do imóvel?"
- "Quanto é a fiança?"
- "Quais são os gastos comuns?"

## Troubleshooting

**Erro: ModuleNotFoundError: No module named 'docling'**
```bash
pip install docling==2.14.0
```

**Erro: API Key não configurada**
```bash
# Verifique se o .env existe e tem a chave correta
cat .env
```

**PDF não processa**
```bash
# Verifique se o arquivo existe e não está protegido
ls -lh contratos/
```

## Próximos Passos

1. Leia [PIPELINE_USAGE.md](PIPELINE_USAGE.md) para documentação completa
2. Explore os módulos em `src/`
3. Adapte o código para suas necessidades
