#!/usr/bin/env python3
"""
Pipeline completo: Docling -> RAG -> CSV -> Busca Semântica

Este script integra todos os componentes para processar contratos
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.docling_processor import DoclingProcessor
from src.rag_engine import RAGEngine
from src.csv_exporter import CSVExporter
from src.semantic_search import SemanticSearch


class ContractPipeline:
    """Pipeline completo de processamento de contratos"""

    def __init__(
        self,
        contracts_dir: str = "contratos",
        output_dir: str = "output",
        db_dir: str = "chromadb_storage"
    ):
        """
        Inicializa o pipeline

        Args:
            contracts_dir: Diretório com PDFs de contratos
            output_dir: Diretório para arquivos de saída
            db_dir: Diretório para banco de dados ChromaDB
        """
        load_dotenv()

        self.contracts_dir = contracts_dir
        self.output_dir = output_dir
        self.db_dir = db_dir

        # Criar diretórios se não existirem
        os.makedirs(contracts_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Inicializar componentes
        print("Inicializando componentes...")
        self.docling = DoclingProcessor()
        self.rag = RAGEngine(persist_directory=db_dir)
        self.exporter = CSVExporter()
        self.search = SemanticSearch(self.rag)

        print("✓ Pipeline inicializado\n")

    def process_single_contract(
        self,
        pdf_path: str,
        contract_id: Optional[str] = None
    ) -> dict:
        """
        Processa um único contrato

        Args:
            pdf_path: Caminho para o PDF
            contract_id: ID do contrato (opcional, usa nome do arquivo)

        Returns:
            Dict com dados processados
        """
        if not contract_id:
            contract_id = Path(pdf_path).stem

        print(f"\n=== Processando contrato: {contract_id} ===")

        # 1. Processar com Docling
        print("1. Extraindo conteúdo com Docling...")
        doc_data = self.docling.process_pdf(pdf_path)
        print(f"   ✓ Extraídas {len(doc_data['sections'])} seções")

        # 2. Indexar no RAG
        print("2. Indexando no sistema RAG...")
        self.rag.index_document(
            doc_data=doc_data,
            contract_id=contract_id,
            metadata={"file_name": doc_data["file_name"]}
        )

        if doc_data.get("sections"):
            self.rag.index_sections(
                sections=doc_data["sections"],
                contract_id=contract_id
            )
        print("   ✓ Contrato indexado")

        # 3. Extrair dados estruturados
        print("3. Extraindo dados estruturados...")
        structured_data = self.exporter.extract_structured_data(
            contract_text=doc_data["full_text"],
            contract_id=contract_id
        )
        print("   ✓ Dados estruturados extraídos")

        return {
            "contract_id": contract_id,
            "doc_data": doc_data,
            "structured_data": structured_data
        }

    def process_all_contracts(self) -> List[dict]:
        """
        Processa todos os PDFs no diretório de contratos

        Returns:
            Lista com dados de todos os contratos processados
        """
        pdf_files = list(Path(self.contracts_dir).glob("*.pdf"))

        if not pdf_files:
            print(f"⚠ Nenhum arquivo PDF encontrado em {self.contracts_dir}")
            return []

        print(f"\nEncontrados {len(pdf_files)} contratos para processar\n")

        all_results = []

        for pdf_file in pdf_files:
            try:
                result = self.process_single_contract(str(pdf_file))
                all_results.append(result)
            except Exception as e:
                print(f"✗ Erro ao processar {pdf_file.name}: {e}")

        return all_results

    def export_to_csv(
        self,
        contracts_data: Optional[List[dict]] = None
    ):
        """
        Exporta contratos para CSV

        Args:
            contracts_data: Lista de dados (opcional, busca do RAG se None)
        """
        print("\n=== Exportando para CSV ===")

        if not contracts_data:
            # Buscar todos os contratos do RAG
            contract_ids = self.rag.get_all_contracts()
            contracts_data = []

            for contract_id in contract_ids:
                # Buscar dados do RAG
                results = self.rag.search_by_contract(
                    query="informações do contrato",
                    contract_id=contract_id,
                    n_results=10
                )

                # Extrair dados estruturados
                full_text = "\n".join(results["documents"])
                structured = self.exporter.extract_structured_data(
                    contract_text=full_text,
                    contract_id=contract_id
                )

                contracts_data.append({"structured_data": structured})

        # Extrair apenas dados estruturados
        structured_list = [c.get("structured_data", c) for c in contracts_data]

        # Exportar
        csv_path = os.path.join(self.output_dir, "contratos_exportados.csv")
        json_path = os.path.join(self.output_dir, "contratos_exportados.json")

        self.exporter.export_to_csv(structured_list, csv_path)
        self.exporter.export_to_json(structured_list, json_path)

        print(f"\n✓ Arquivos exportados em {self.output_dir}/")

    def search_interactive(self):
        """Inicia modo de busca interativa"""
        self.search.interactive_search()

    def demo_search(self):
        """Demonstração de busca semântica"""
        print("\n=== DEMONSTRAÇÃO DE BUSCA SEMÂNTICA ===\n")

        contracts = self.rag.get_all_contracts()

        if not contracts:
            print("⚠ Nenhum contrato indexado ainda")
            return

        print(f"Contratos indexados: {', '.join(contracts)}\n")

        # Perguntas exemplo
        example_queries = [
            "Qual é o valor da renda mensal?",
            "Quem é o arrendador?",
            "Qual é a duração do contrato?",
            "Qual é o endereço do imóvel?",
        ]

        contract_id = contracts[0]
        print(f"Fazendo perguntas sobre o contrato: {contract_id}\n")

        for query in example_queries:
            print(f"Pergunta: {query}")
            answer = self.search.ask_question(query, contract_id)
            print(f"Resposta: {answer}\n")
            print("-" * 60 + "\n")


def main():
    """Função principal com menu interativo"""
    pipeline = ContractPipeline()

    while True:
        print("\n" + "="*60)
        print("PIPELINE DE PROCESSAMENTO DE CONTRATOS")
        print("="*60)
        print("\n1. Processar todos os contratos (Docling + RAG)")
        print("2. Processar contrato específico")
        print("3. Exportar para CSV")
        print("4. Busca semântica (modo interativo)")
        print("5. Demo de busca semântica")
        print("6. Listar contratos indexados")
        print("7. Gerar resumo de contrato")
        print("0. Sair")
        print("\n" + "-"*60)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            results = pipeline.process_all_contracts()
            if results:
                print(f"\n✓ Processados {len(results)} contratos")

                # Perguntar se quer exportar
                export = input("\nDeseja exportar para CSV? (s/n): ").strip().lower()
                if export == 's':
                    pipeline.export_to_csv(results)

        elif opcao == "2":
            pdf_path = input("\nCaminho do PDF: ").strip()
            contract_id = input("ID do contrato (Enter para usar nome do arquivo): ").strip()

            if os.path.exists(pdf_path):
                result = pipeline.process_single_contract(
                    pdf_path,
                    contract_id if contract_id else None
                )
                print(f"\n✓ Contrato {result['contract_id']} processado")
            else:
                print(f"✗ Arquivo não encontrado: {pdf_path}")

        elif opcao == "3":
            pipeline.export_to_csv()

        elif opcao == "4":
            pipeline.search_interactive()

        elif opcao == "5":
            pipeline.demo_search()

        elif opcao == "6":
            contracts = pipeline.rag.get_all_contracts()
            if contracts:
                print(f"\nContratos indexados ({len(contracts)}):")
                for i, contract_id in enumerate(contracts, 1):
                    print(f"  {i}. {contract_id}")
            else:
                print("\n⚠ Nenhum contrato indexado")

        elif opcao == "7":
            contracts = pipeline.rag.get_all_contracts()
            if not contracts:
                print("\n⚠ Nenhum contrato indexado")
                continue

            print("\nContratos disponíveis:")
            for i, cid in enumerate(contracts, 1):
                print(f"  {i}. {cid}")

            contract_id = input("\nID do contrato: ").strip()
            if contract_id in contracts:
                summary = pipeline.search.get_contract_summary(contract_id)
                print(f"\n{summary}")
            else:
                print(f"✗ Contrato '{contract_id}' não encontrado")

        elif opcao == "0":
            print("\nEncerrando...")
            break

        else:
            print("\n✗ Opção inválida")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     PIPELINE DE PROCESSAMENTO DE CONTRATOS                   ║
    ║                                                              ║
    ║     Docling → RAG → CSV → Busca Semântica                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
