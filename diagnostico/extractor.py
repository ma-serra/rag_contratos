"""
Sistema de Extração de Dados usando RAG + Claude AI
Analisa documentos condominiais e extrai informações estruturadas
"""

import os
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from .database import CondominioDatabase

load_dotenv()


class CondominioExtractor:
    """Extrai e analisa dados de documentos condominiais usando RAG"""

    def __init__(self, database: CondominioDatabase):
        """
        Args:
            database: Instância do CondominioDatabase
        """
        self.db = database
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def extract_fase1_identificacao(
        self,
        condominio_id: str,
        query_custom: Optional[str] = None
    ) -> Dict:
        """
        FASE 1: Identificação e Extração Jurídica
        Extrai dados constitutivos obrigatórios

        Args:
            condominio_id: ID do condomínio
            query_custom: Query personalizada (opcional)

        Returns:
            Dicionário com dados extraídos
        """
        # Queries para buscar informações relevantes
        queries = query_custom or [
            "denominação social, CNPJ, endereço, registro de imóveis, matrícula",
            "unidades autônomas, metragem, frações ideais, áreas comuns",
            "estrutura administrativa, síndico, conselho, mandatos, competências"
        ]

        if isinstance(queries, str):
            queries = [queries]

        # Buscar chunks relevantes
        all_chunks = []
        for query in queries:
            results = self.db.search(
                query=query,
                condominio_id=condominio_id,
                doc_types=["convencoes", "normas"],
                n_results=5
            )
            all_chunks.extend(results)

        # Consolidar contexto
        context = self._build_context(all_chunks)

        # Prompt para Claude
        prompt = f"""
Analise os documentos do condomínio e extraia as seguintes informações em formato JSON:

FASE 1 - IDENTIFICAÇÃO E EXTRAÇÃO JURÍDICA

Extraia:
1.1 IDENTIFICAÇÃO REGISTRAL:
   - Denominação social completa
   - CNPJ e inscrições (municipal/estadual)
   - Endereço completo com CEP
   - Matrícula do Registro de Imóveis
   - Data de instituição

1.2 ESTRUTURA FÍSICO-JURÍDICA:
   - Tipologia (residencial/comercial/misto)
   - Quantidade de unidades autônomas
   - Sistema de frações ideais
   - Áreas comuns principais
   - Vagas de garagem

1.3 GOVERNANÇA:
   - Estrutura administrativa
   - Mandatos e competências
   - Quóruns de decisão

DOCUMENTOS:
{context}

Retorne APENAS um JSON válido seguindo esta estrutura:
{{
  "identificacao_registral": {{
    "denominacao": "",
    "cnpj": "",
    "endereco": "",
    "matricula": "",
    "data_instituicao": ""
  }},
  "estrutura_fisica": {{
    "tipologia": "",
    "unidades_autonomas": 0,
    "fracoes_ideais": "",
    "areas_comuns": [],
    "vagas_garagem": ""
  }},
  "governanca": {{
    "estrutura_administrativa": [],
    "mandatos": "",
    "quoruns": {{}}
  }}
}}
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            return json.loads(result_text)

        except Exception as e:
            print(f"Erro na extração: {e}")
            return {"error": str(e)}

    def extract_fase2_mapeamento(
        self,
        condominio_id: str
    ) -> Dict:
        """
        FASE 2: Mapeamento Hierárquico e Classificação Normativa
        Identifica estrutura de artigos e disposições

        Args:
            condominio_id: ID do condomínio

        Returns:
            Mapeamento hierárquico de normas
        """
        # Buscar toda a convenção
        results = self.db.search(
            query="artigos, capítulos, títulos, disposições",
            condominio_id=condominio_id,
            doc_types=["convencoes", "normas"],
            n_results=10
        )

        context = self._build_context(results)

        prompt = f"""
Analise a convenção/regimento e crie um MAPEAMENTO HIERÁRQUICO das disposições normativas.

Classifique cada artigo/seção em:

1. DISPOSIÇÕES CONSTITUTIVAS (Alteração: unanimidade)
   - Denominação, frações ideais, partes comuns essenciais

2. DISPOSIÇÕES ADMINISTRATIVAS (Alteração: maioria qualificada)
   - Órgãos, competências, assembleias

3. DISPOSIÇÕES REGULAMENTARES (Alteração: maioria simples)
   - Uso de áreas, convivência, penalidades

4. DISPOSIÇÕES ECONÔMICO-FINANCEIRAS
   - Contribuições, fundos, inadimplemento

DOCUMENTOS:
{context}

Retorne JSON:
{{
  "disposicoes_constitutivas": [
    {{"artigo": "", "conteudo": "", "fundamento_legal": ""}}
  ],
  "disposicoes_administrativas": [],
  "disposicoes_regulamentares": [],
  "disposicoes_economicas": [],
  "problemas_identificados": {{
    "conflitos_normativos": [],
    "lacunas": [],
    "vicios_quorum": []
  }}
}}
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            return json.loads(response.content[0].text)

        except Exception as e:
            return {"error": str(e)}

    def extract_fase3_conformidade(
        self,
        condominio_id: str
    ) -> Dict:
        """
        FASE 3: Matriz de Conformidade Legal
        Audita conformidade com legislação

        Args:
            condominio_id: ID do condomínio

        Returns:
            Matriz de conformidade
        """
        results = self.db.search(
            query="penalidades, quórum, frações ideais, assembleia, multa",
            condominio_id=condominio_id,
            doc_types=["convencoes", "normas"],
            n_results=8
        )

        context = self._build_context(results)

        prompt = f"""
Audite a CONFORMIDADE LEGAL da convenção/regimento com a legislação brasileira.

Base legal:
- Lei 4.591/64 (Condomínios)
- Código Civil arts. 1.331 a 1.358
- Jurisprudência do STJ

Avalie:
1. LEGALIDADE ESTRITA
   - Frações ideais (Lei 4.591/64, art. 1º, §3º)
   - Quóruns assembleia (CC art. 1.352)
   - Penalidades (CC art. 1.337)
   - Destinação unidades

2. ADEQUAÇÃO FORMAL
   - Competência deliberativa
   - Procedimentos de alteração
   - Publicidade e vigência

3. EFICÁCIA JURÍDICA
   - Exequibilidade das normas
   - Proporcionalidade de penalidades
   - Razoabilidade

DOCUMENTOS:
{context}

Retorne JSON:
{{
  "conformidade": [
    {{
      "aspecto": "",
      "status": "CONFORME/DESCONFORME",
      "dispositivo_legal": "",
      "consequencia": "",
      "acao_recomendada": "MANTER/REFORMULAR/ADEQUAR/SUPRIMIR/COMPLEMENTAR"
    }}
  ],
  "problemas_criticos": [],
  "recomendacoes_prioritarias": []
}}
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            return json.loads(response.content[0].text)

        except Exception as e:
            return {"error": str(e)}

    def diagnostico_completo(
        self,
        condominio_id: str,
        objetivo: str = "REVISAO_CONFORMIDADE"
    ) -> Dict:
        """
        Executa diagnóstico completo do condomínio

        Args:
            condominio_id: ID do condomínio
            objetivo: REGIMENTO_INTERNO, ANALISE_PENALIDADES, REVISAO_CONFORMIDADE, OTIMIZACAO_GERAL

        Returns:
            Relatório completo do diagnóstico
        """
        print(f"\n🔍 Iniciando Diagnóstico Condominial - {objetivo}")
        print(f"Condomínio ID: {condominio_id}\n")

        resultado = {
            "condominio_id": condominio_id,
            "objetivo": objetivo,
            "fases": {}
        }

        # Executar fases conforme objetivo
        if objetivo in ["REGIMENTO_INTERNO", "REVISAO_CONFORMIDADE", "OTIMIZACAO_GERAL"]:
            print("📋 Executando FASE 1 - Identificação e Extração...")
            resultado["fases"]["fase1_identificacao"] = self.extract_fase1_identificacao(condominio_id)

        if objetivo in ["ANALISE_PENALIDADES", "REVISAO_CONFORMIDADE", "OTIMIZACAO_GERAL"]:
            print("📊 Executando FASE 2 - Mapeamento Hierárquico...")
            resultado["fases"]["fase2_mapeamento"] = self.extract_fase2_mapeamento(condominio_id)

        if objetivo in ["ANALISE_PENALIDADES", "REVISAO_CONFORMIDADE", "OTIMIZACAO_GERAL"]:
            print("⚖️  Executando FASE 3 - Conformidade Legal...")
            resultado["fases"]["fase3_conformidade"] = self.extract_fase3_conformidade(condominio_id)

        print("\n✅ Diagnóstico concluído!\n")
        return resultado

    def _build_context(self, chunks: List[Dict], max_length: int = 8000) -> str:
        """
        Constrói contexto a partir dos chunks recuperados

        Args:
            chunks: Lista de chunks do RAG
            max_length: Tamanho máximo do contexto

        Returns:
            Contexto formatado
        """
        if not chunks:
            return "Nenhum documento encontrado."

        context_parts = []
        current_length = 0

        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})

            chunk_text = f"""
--- Documento {i+1} ---
Tipo: {metadata.get('doc_type', 'N/A')}
Documento: {metadata.get('document_name', 'N/A')}
Seção: {metadata.get('section', 'N/A')}

{content}
"""

            if current_length + len(chunk_text) > max_length:
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        return "\n".join(context_parts)
