"""
Interface de busca semântica para contratos
"""
import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from .rag_engine import RAGEngine


class SemanticSearch:
    """Interface de busca semântica com geração de respostas"""

    def __init__(
        self,
        rag_engine: RAGEngine,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Inicializa a interface de busca

        Args:
            rag_engine: Motor RAG configurado
            anthropic_api_key: Chave da API Anthropic
        """
        self.rag = rag_engine
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.api_key:
            self.anthropic = Anthropic(api_key=self.api_key)
        else:
            self.anthropic = None

    def search(
        self,
        query: str,
        contract_id: Optional[str] = None,
        n_results: int = 5,
        use_llm: bool = True
    ) -> Dict:
        """
        Realiza busca semântica e opcionalmente gera resposta com LLM

        Args:
            query: Pergunta ou consulta
            contract_id: ID do contrato (opcional, para busca específica)
            n_results: Número de resultados
            use_llm: Se True, usa Claude para gerar resposta

        Returns:
            Dict com resultados e resposta gerada
        """
        # Buscar contexto relevante
        if contract_id:
            search_results = self.rag.search_by_contract(
                query=query,
                contract_id=contract_id,
                n_results=n_results
            )
        else:
            search_results = self.rag.search(
                query=query,
                n_results=n_results
            )

        response = {
            "query": query,
            "contract_id": contract_id,
            "search_results": search_results,
            "llm_response": None
        }

        # Gerar resposta com LLM se solicitado
        if use_llm and self.anthropic:
            llm_response = self._generate_answer(query, search_results)
            response["llm_response"] = llm_response

        return response

    def _generate_answer(
        self,
        query: str,
        search_results: Dict
    ) -> str:
        """
        Gera resposta usando Claude baseada nos resultados da busca

        Args:
            query: Pergunta do usuário
            search_results: Resultados da busca semântica

        Returns:
            Resposta gerada
        """
        # Preparar contexto
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            search_results["documents"],
            search_results["metadatas"]
        )):
            context_parts.append(f"[Trecho {i+1}]")
            context_parts.append(doc)
            context_parts.append("")

        context = "\n".join(context_parts)

        # Criar prompt
        prompt = f"""
        Com base nos seguintes trechos de um contrato de aluguel, responda à pergunta do usuário de forma clara e precisa.

        Trechos do contrato:
        {context}

        Pergunta: {query}

        Instruções:
        1. Use APENAS as informações dos trechos fornecidos
        2. Se a informação não estiver nos trechos, diga "Não encontrei essa informação no contrato"
        3. Seja específico e cite valores exatos quando disponíveis
        4. Responda em português de forma clara e objetiva
        """

        try:
            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"Erro ao gerar resposta: {e}"

    def ask_question(
        self,
        question: str,
        contract_id: Optional[str] = None
    ) -> str:
        """
        Faz uma pergunta e retorna resposta direta

        Args:
            question: Pergunta
            contract_id: ID do contrato (opcional)

        Returns:
            Resposta em texto
        """
        result = self.search(
            query=question,
            contract_id=contract_id,
            n_results=3,
            use_llm=True
        )

        return result.get("llm_response", "Não foi possível gerar resposta")

    def get_contract_summary(self, contract_id: str) -> str:
        """
        Gera resumo de um contrato

        Args:
            contract_id: ID do contrato

        Returns:
            Resumo do contrato
        """
        if not self.anthropic:
            return "API do Anthropic não configurada"

        # Buscar informações principais
        queries = [
            "Quem é o arrendador?",
            "Quem são os arrendatários?",
            "Qual é o endereço do imóvel?",
            "Qual é o valor da renda mensal?",
            "Qual é a duração do contrato?"
        ]

        summary_parts = [f"=== RESUMO DO CONTRATO {contract_id} ===\n"]

        for query in queries:
            answer = self.ask_question(query, contract_id)
            summary_parts.append(f"• {query}")
            summary_parts.append(f"  {answer}\n")

        return "\n".join(summary_parts)

    def compare_contracts(
        self,
        contract_ids: List[str],
        aspect: str = "condições econômicas"
    ) -> str:
        """
        Compara aspectos de diferentes contratos

        Args:
            contract_ids: Lista de IDs de contratos
            aspect: Aspecto a comparar

        Returns:
            Comparação em texto
        """
        if not self.anthropic:
            return "API do Anthropic não configurada"

        comparison_parts = [f"=== COMPARAÇÃO: {aspect.upper()} ===\n"]

        for contract_id in contract_ids:
            comparison_parts.append(f"\n[Contrato {contract_id}]")
            answer = self.ask_question(
                f"Quais são {aspect}?",
                contract_id
            )
            comparison_parts.append(answer)

        return "\n".join(comparison_parts)

    def batch_search(
        self,
        queries: List[str],
        contract_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Realiza múltiplas buscas em lote

        Args:
            queries: Lista de perguntas
            contract_id: ID do contrato (opcional)

        Returns:
            Lista de resultados
        """
        results = []

        for query in queries:
            result = self.search(
                query=query,
                contract_id=contract_id,
                use_llm=True
            )
            results.append(result)

        return results

    def interactive_search(self):
        """Modo interativo de busca"""
        print("\n=== BUSCA SEMÂNTICA DE CONTRATOS ===")
        print("Digite 'sair' para encerrar\n")

        # Listar contratos disponíveis
        contracts = self.rag.get_all_contracts()
        if contracts:
            print(f"Contratos disponíveis: {', '.join(contracts)}\n")
        else:
            print("Nenhum contrato indexado ainda.\n")

        while True:
            # Perguntar se quer buscar em contrato específico
            contract_id = input("ID do contrato (Enter para buscar em todos): ").strip()
            if contract_id.lower() == 'sair':
                break

            if contract_id and contract_id not in contracts and contracts:
                print(f"Contrato '{contract_id}' não encontrado.\n")
                continue

            # Pergunta
            query = input("\nSua pergunta: ").strip()
            if query.lower() == 'sair':
                break

            if not query:
                continue

            # Buscar
            print("\nBuscando...\n")
            answer = self.ask_question(
                query,
                contract_id if contract_id else None
            )

            print(f"Resposta:\n{answer}\n")
            print("-" * 60)


if __name__ == "__main__":
    # Exemplo de uso
    rag = RAGEngine()
    search = SemanticSearch(rag)

    print("SemanticSearch inicializado")
    print("Use search.interactive_search() para modo interativo")
